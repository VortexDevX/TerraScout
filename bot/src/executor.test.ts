import { describe, expect, it, vi } from 'vitest';
import { executeCommand } from './executor.js';
import type { ActionCommand } from './protocol.js';

function fakeBot() {
  return {
    entity: { position: { x: 0, y: 64, z: 0 } },
    entities: {},
    blockAt: () => ({ name: 'grass_block', light: 15 }),
    pathfinder: {
      stop: vi.fn(),
      goto: vi.fn().mockResolvedValue(undefined),
    },
  };
}

describe('executeCommand', () => {
  it('idles without movement', async () => {
    const bot = fakeBot();
    const command: ActionCommand = {
      command_id: 'cmd-1',
      command: 'idle',
      reason: 'test',
      max_duration_ms: 100,
    };

    const result = await executeCommand(bot as never, command);

    expect(result.ok).toBe(true);
    expect(bot.pathfinder.stop).toHaveBeenCalled();
    expect(bot.pathfinder.goto).not.toHaveBeenCalled();
  });
});

