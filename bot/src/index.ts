import mineflayer from 'mineflayer';
import WebSocket from 'ws';
import { loadConfig } from './config.js';
import { executeCommand } from './executor.js';
import { observe } from './observer.js';
import { Movements, pathfinder } from './pathfinder.js';
import type { ActionCommand, Envelope } from './protocol.js';
import { envelope } from './protocol.js';

const config = loadConfig();
const bot = mineflayer.createBot({
  host: config.minecraftHost,
  port: config.minecraftPort,
  username: config.minecraftUsername,
  version: config.minecraftVersion,
});

bot.loadPlugin(pathfinder);

let backend: WebSocket | null = null;
let lastPathfindingError: string | null = null;
let activeCommandId: string | null = null;

function send<T>(type: string, payload: T): void {
  if (!backend || backend.readyState !== WebSocket.OPEN) return;
  backend.send(JSON.stringify(envelope(type, payload)));
}

function connectBackend(): void {
  backend = new WebSocket(config.backendWs);

  backend.on('open', () => {
    console.log(`Connected backend ${config.backendWs}`);
  });

  backend.on('message', async (data) => {
    const message = JSON.parse(data.toString()) as Envelope<ActionCommand | { message?: string }>;
    if (message.type === 'command') {
      const command = message.payload as ActionCommand;
      if (activeCommandId && command.command === 'idle') {
        bot.pathfinder.stop();
        activeCommandId = null;
      } else if (activeCommandId && command.command === 'report_state') {
        send('execution_result', {
          command_id: command.command_id,
          ok: true,
          message: `status while active command ${activeCommandId} runs`,
          position: {
            x: bot.entity.position.x,
            y: bot.entity.position.y,
            z: bot.entity.position.z,
          },
        });
        return;
      } else if (activeCommandId && command.command !== 'report_state') {
        send('execution_result', {
          command_id: command.command_id,
          ok: true,
          message: `ignored while active command ${activeCommandId} runs`,
          position: {
            x: bot.entity.position.x,
            y: bot.entity.position.y,
            z: bot.entity.position.z,
          },
        });
        return;
      }
      activeCommandId = command.command_id;
      const result = await executeCommand(bot, command);
      activeCommandId = null;
      if (!result.ok && !result.message.startsWith('ignored while active command')) {
        lastPathfindingError = result.message;
      }
      send('execution_result', result);
      return;
    }
    if (message.type === 'error') {
      console.error('Backend error', message.payload);
    }
  });

  backend.on('close', () => {
    console.error('Backend disconnected; reconnecting soon');
    setTimeout(connectBackend, 2000);
  });

  backend.on('error', (error) => {
    console.error('Backend websocket error', error.message);
  });
}

bot.once('spawn', () => {
  const defaultMovements = new Movements(bot);
  defaultMovements.canDig = false;
  defaultMovements.allow1by1towers = false;
  defaultMovements.allowFreeMotion = false;
  defaultMovements.allowParkour = false;
  defaultMovements.allowSprinting = false;
  defaultMovements.allowEntityDetection = true;
  defaultMovements.maxDropDown = 1;
  for (const blockName of ['lava', 'water', 'fire', 'cactus']) {
    const block = bot.registry.blocksByName[blockName];
    if (block) defaultMovements.blocksToAvoid.add(block.id);
  }
  for (const entityName of ['zombie', 'skeleton', 'creeper', 'spider', 'witch', 'enderman', 'drowned']) {
    defaultMovements.entitiesToAvoid.add(entityName);
  }
  bot.pathfinder.setMovements(defaultMovements);

  connectBackend();
  setInterval(() => {
    send('observation', observe(bot, lastPathfindingError));
    lastPathfindingError = null;
  }, config.observationIntervalMs);
});

bot.on('kicked', (reason) => console.error('Kicked', reason));
bot.on('error', (error) => console.error('Bot error', error.message));
