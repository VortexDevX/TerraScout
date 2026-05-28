import type { Bot } from 'mineflayer';
import type { Position } from './protocol.js';

const HOSTILE_NAMES = new Set([
  'zombie',
  'skeleton',
  'creeper',
  'spider',
  'witch',
  'enderman',
  'drowned',
  'husk',
  'stray',
  'pillager',
]);

export function isHostile(name: string | undefined): boolean {
  return !!name && HOSTILE_NAMES.has(name);
}

export function toPosition(position: { x: number; y: number; z: number }): Position {
  return { x: position.x, y: position.y, z: position.z };
}

export function hasNearbyBlock(bot: Bot, names: Set<string>, radius: number): boolean {
  const origin = bot.entity.position.floored();
  for (let x = -radius; x <= radius; x += 1) {
    for (let y = -2; y <= 1; y += 1) {
      for (let z = -radius; z <= radius; z += 1) {
        const block = bot.blockAt(origin.offset(x, y, z));
        if (block && names.has(block.name)) return true;
      }
    }
  }
  return false;
}

export function hasNearbyCliff(bot: Bot, radius: number): boolean {
  const origin = bot.entity.position.floored();
  for (let x = -radius; x <= radius; x += 1) {
    for (let z = -radius; z <= radius; z += 1) {
      const below = bot.blockAt(origin.offset(x, -1, z));
      const deepBelow = bot.blockAt(origin.offset(x, -4, z));
      if (!below && !deepBelow) return true;
    }
  }
  return false;
}

export function targetIsUnsafe(bot: Bot, target: Position): string | null {
  const nearbyHostile = Object.values(bot.entities).find((entity) => {
    return isHostile(entity.name) && entity.position.distanceTo(bot.entity.position) <= 8;
  });
  if (nearbyHostile) return `hostile nearby: ${nearbyHostile.name}`;
  if (hasNearbyBlock(bot, new Set(['lava']), 3)) return 'lava nearby';
  if (hasNearbyCliff(bot, 2)) return 'cliff nearby';
  if (hasNearbyBlock(bot, new Set(['water']), 2) && target.y < bot.entity.position.y - 1) {
    return 'deep water risk';
  }
  return null;
}

