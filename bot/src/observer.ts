import type { Bot } from 'mineflayer';
import type { Observation } from './protocol.js';
import { hasNearbyBlock, hasNearbyCliff, isHostile, toPosition } from './safety.js';

export function observe(bot: Bot, pathfindingError: string | null = null): Observation {
  const position = bot.entity.position;
  const hostileEntities = Object.values(bot.entities)
    .filter((entity) => isHostile(entity.name))
    .map((entity) => ({
      kind: entity.name ?? 'unknown',
      position: toPosition(entity.position),
      distance: entity.position.distanceTo(position),
    }))
    .filter((mob) => mob.distance <= 16)
    .slice(0, 10);

  const block = bot.blockAt(position.floored());
  return {
    bot_id: bot.username,
    position: toPosition(position),
    biome: block?.biome?.name ?? 'unknown',
    health: bot.health,
    hunger: bot.food,
    time_of_day: bot.time.timeOfDay,
    light_level: block?.light ?? 0,
    nearby_hostiles: hostileEntities,
    nearby_lava: hasNearbyBlock(bot, new Set(['lava']), 4),
    nearby_cliff: hasNearbyCliff(bot, 3),
    nearby_deep_water: hasNearbyBlock(bot, new Set(['water']), 3),
    pathfinding_error: pathfindingError,
  };
}

