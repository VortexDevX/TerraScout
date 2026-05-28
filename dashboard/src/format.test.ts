import { describe, expect, it } from 'vitest';
import { formatPosition } from './format';
import type { TelemetrySnapshot } from './types';

describe('formatPosition', () => {
  it('formats coordinates to one decimal', () => {
    const snapshot = {
      observation: {
        bot_id: 'bot',
        position: { x: 1.234, y: 64, z: -5.678 },
        biome: 'plains',
        health: 20,
        hunger: 20,
        time_of_day: 6000,
        light_level: 15,
      },
    } as TelemetrySnapshot;

    expect(formatPosition(snapshot)).toBe('1.2, 64.0, -5.7');
  });

  it('handles missing observation', () => {
    expect(formatPosition(null)).toBe('unknown');
  });
});

