import type { Bot } from 'mineflayer';
import { Vec3 } from 'vec3';
import type { Observation, TerrainSample } from './protocol.js';
import { hasNearbyBlock, hasNearbyCliff, isHostile, toPosition } from './safety.js';

function readBiomeName(bot: Bot): string {
  const biomeId = bot.world.getBiome(bot.entity.position.floored());
  const biome = bot.registry.biomes[biomeId];
  return biome?.name ?? 'unknown';
}

function readLightLevel(bot: Bot): number {
  const position = bot.entity.position.floored();
  const blockLight = bot.world.getBlockLight(position) ?? 0;
  const skyLight = bot.world.getSkyLight(position) ?? 0;
  return Math.max(blockLight, skyLight);
}

function biomeNameAt(bot: Bot, position: Vec3): string {
  const biomeId = bot.world.getBiome(position);
  return bot.registry.biomes[biomeId]?.name ?? 'unknown';
}

function findSurfaceSample(bot: Bot, x: number, z: number): TerrainSample | null {
  const origin = bot.entity.position.floored();
  for (let y = origin.y + 10; y >= origin.y - 14; y -= 1) {
    const position = new Vec3(x, y, z);
    const block = bot.blockAt(position);
    if (!block) continue;
    if (block.boundingBox === 'empty' && block.name !== 'water' && block.name !== 'lava') continue;
    const above = bot.blockAt(position.offset(0, 1, 0));
    const isWater = block.name === 'water';
    const isLava = block.name === 'lava';
    const isPassable = !isLava && !['fire', 'cactus'].includes(block.name) && (!above || above.boundingBox === 'empty');
    return {
      position: toPosition(position),
      top_block: block.name,
      biome: biomeNameAt(bot, position),
      elevation_delta: y - origin.y,
      is_water: isWater,
      is_lava: isLava,
      is_passable: isPassable,
    };
  }
  return null;
}

function sampleTerrain(bot: Bot): TerrainSample[] {
  const origin = bot.entity.position.floored();
  const samples: TerrainSample[] = [];
  for (const dx of [-12, -6, 0, 6, 12]) {
    for (const dz of [-12, -6, 0, 6, 12]) {
      const sample = findSurfaceSample(bot, origin.x + dx, origin.z + dz);
      if (sample) samples.push(sample);
    }
  }
  return samples;
}

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
  const floor = bot.blockAt(position.floored().offset(0, -1, 0));
  return {
    bot_id: bot.username,
    position: toPosition(position),
    biome: readBiomeName(bot),
    health: bot.health,
    hunger: bot.food,
    time_of_day: bot.time.timeOfDay,
    light_level: readLightLevel(bot),
    nearby_hostiles: hostileEntities,
    nearby_lava: hasNearbyBlock(bot, new Set(['lava']), 4),
    nearby_cliff: hasNearbyCliff(bot, 3),
    nearby_deep_water: hasNearbyBlock(bot, new Set(['water']), 3),
    feet_block: block?.name ?? null,
    floor_block: floor?.name ?? null,
    pathfinding_error: pathfindingError,
    terrain_samples: sampleTerrain(bot),
  };
}
