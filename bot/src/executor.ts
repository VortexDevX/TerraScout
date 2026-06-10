import type { Bot } from 'mineflayer';
import type { ActionCommand, ExecutionResult, Position } from './protocol.js';
import { goals } from './pathfinder.js';
import { findSafeNearbyTarget, targetIsUnsafe, toPosition } from './safety.js';

function result(command: ActionCommand, ok: boolean, message: string, position?: Position): ExecutionResult {
  return {
    command_id: command.command_id,
    ok,
    message,
    position,
  };
}

export async function executeCommand(bot: Bot, command: ActionCommand): Promise<ExecutionResult> {
  if (command.command === 'report_state') {
    return result(command, true, command.command, toPosition(bot.entity.position));
  }

  if (command.command === 'idle') {
    bot.pathfinder.stop();
    return result(command, true, command.command, toPosition(bot.entity.position));
  }

  const fallbackRadius = command.command === 'flee' ? 12 : 8;
  const radius = command.radius ?? fallbackRadius;
  const target = command.target ?? findSafeNearbyTarget(bot, radius);
  if (!target) {
    return result(command, false, `${command.command} found no safe nearby target`, toPosition(bot.entity.position));
  }

  const unsafeReason = targetIsUnsafe(bot, target);
  if (unsafeReason) {
    bot.pathfinder.stop();
    return result(command, false, `safe movement stopped: ${unsafeReason}`, toPosition(bot.entity.position));
  }

  const goal = new goals.GoalNearXZ(target.x, target.z, 1);
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<ExecutionResult>((resolve) => {
    timeoutId = setTimeout(() => {
      bot.pathfinder.stop();
      resolve(result(command, false, `pathfinding timeout toward ${target.x},${target.z}`, toPosition(bot.entity.position)));
    }, command.max_duration_ms);
  });

  const movement = bot.pathfinder.goto(goal).then(
    () => result(command, true, `movement complete toward ${target.x},${target.z}`, toPosition(bot.entity.position)),
    (error: unknown) => {
      bot.pathfinder.stop();
      return result(command, false, `pathfinding failed: ${String(error)}`, toPosition(bot.entity.position));
    },
  );

  const outcome = await Promise.race([movement, timeout]);
  if (timeoutId) clearTimeout(timeoutId);
  return outcome;
}
