import type { Bot } from 'mineflayer';
import { Vec3 } from 'vec3';
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

function targetBlockRisk(bot: Bot, target: Position): string | null {
  const x = Math.floor(target.x);
  const y = Math.floor(target.y);
  const z = Math.floor(target.z);
  const position = new Vec3(x, y, z);
  const foot = bot.blockAt(position);
  let below = bot.blockAt(position.offset(0, -1, 0));
  for (let drop = 1; drop <= 2 && (!below || below.boundingBox === 'empty'); drop += 1) {
    below = bot.blockAt(position.offset(0, -1 - drop, 0));
  }
  if (!below || below.boundingBox === 'empty') return 'target has no known floor';
  if (foot && ['lava', 'water'].includes(foot.name)) return `target block is ${foot.name}`;
  if (['lava', 'water'].includes(below.name)) return `target floor is ${below.name}`;
  return null;
}

export function targetIsUnsafe(bot: Bot, target: Position): string | null {
  const nearbyHostile = Object.values(bot.entities).find((entity) => {
    return isHostile(entity.name) && entity.position.distanceTo(bot.entity.position) <= 8;
  });
  if (nearbyHostile) return `hostile nearby: ${nearbyHostile.name}`;
  if (hasNearbyBlock(bot, new Set(['lava']), 3)) return 'lava nearby';
  const targetRisk = targetBlockRisk(bot, target);
  if (targetRisk) return targetRisk;
  if (hasNearbyBlock(bot, new Set(['water']), 2) && target.y < bot.entity.position.y - 1) {
    return 'deep water risk';
  }
  return null;
}

function hasSolidFloorAt(bot: Bot, x: number, y: number, z: number): boolean {
  for (let drop = 1; drop <= 3; drop += 1) {
    const floor = bot.blockAt(new Vec3(x, y - drop, z));
    const feet = bot.blockAt(new Vec3(x, y - drop + 1, z));
    const head = bot.blockAt(new Vec3(x, y - drop + 2, z));
    if (!floor || floor.boundingBox === 'empty') continue;
    if (['lava', 'water', 'fire', 'cactus'].includes(floor.name)) return false;
    if (feet && feet.boundingBox !== 'empty') continue;
    if (head && head.boundingBox !== 'empty') continue;
    return true;
  }
  return false;
}

export function findSafeNearbyTarget(bot: Bot, radius: number): Position | null {
  const origin = bot.entity.position.floored();
  const candidates: Position[] = [];
  for (let dx = -radius; dx <= radius; dx += 2) {
    for (let dz = -radius; dz <= radius; dz += 2) {
      const distance = Math.sqrt(dx * dx + dz * dz);
      if (distance < 4 || distance > radius) continue;
      const x = origin.x + dx;
      const z = origin.z + dz;
      if (hasSolidFloorAt(bot, x, origin.y, z)) {
        candidates.push({ x, y: origin.y, z });
      }
    }
  }
  candidates.sort((a, b) => b.x + b.z - (a.x + a.z));
  return candidates[0] ?? null;
}
