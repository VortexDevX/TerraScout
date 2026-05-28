import type { Bot } from 'mineflayer';
import { goals } from 'mineflayer-pathfinder';
import type { ActionCommand, ExecutionResult, Position } from './protocol.js';
import { targetIsUnsafe, toPosition } from './safety.js';

function result(command: ActionCommand, ok: boolean, message: string, position?: Position): ExecutionResult {
  return {
    command_id: command.command_id,
    ok,
    message,
    position,
  };
}

export async function executeCommand(bot: Bot, command: ActionCommand): Promise<ExecutionResult> {
  if (command.command === 'idle' || command.command === 'report_state') {
    bot.pathfinder.stop();
    return result(command, true, command.command, toPosition(bot.entity.position));
  }

  if (!command.target) {
    return result(command, false, `${command.command} requires target`, toPosition(bot.entity.position));
  }

  const unsafeReason = targetIsUnsafe(bot, command.target);
  if (unsafeReason) {
    bot.pathfinder.stop();
    return result(command, false, `safe movement stopped: ${unsafeReason}`, toPosition(bot.entity.position));
  }

  const goal = new goals.GoalNear(command.target.x, command.target.y, command.target.z, 2);
  const timeout = new Promise<ExecutionResult>((resolve) => {
    setTimeout(() => {
      bot.pathfinder.stop();
      resolve(result(command, false, 'pathfinding timeout', toPosition(bot.entity.position)));
    }, command.max_duration_ms);
  });

  const movement = bot.pathfinder.goto(goal).then(
    () => result(command, true, 'movement complete', toPosition(bot.entity.position)),
    (error: unknown) => {
      bot.pathfinder.stop();
      return result(command, false, `pathfinding failed: ${String(error)}`, toPosition(bot.entity.position));
    },
  );

  return Promise.race([movement, timeout]);
}

