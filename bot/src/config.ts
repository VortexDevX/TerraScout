export type BotConfig = {
  minecraftHost: string;
  minecraftPort: number;
  minecraftUsername: string;
  minecraftVersion?: string;
  backendWs: string;
  observationIntervalMs: number;
};

function intEnv(name: string, fallback: number): number {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = Number.parseInt(raw, 10);
  if (Number.isNaN(parsed)) {
    throw new Error(`${name} must be an integer`);
  }
  return parsed;
}

export function loadConfig(): BotConfig {
  return {
    minecraftHost: process.env.MINECRAFT_HOST ?? '127.0.0.1',
    minecraftPort: intEnv('MINECRAFT_PORT', 25565),
    minecraftUsername: process.env.MINECRAFT_USERNAME ?? 'TerraScout',
    minecraftVersion: process.env.MINECRAFT_VERSION || undefined,
    backendWs: process.env.TERRASCOUT_BACKEND_WS ?? 'ws://127.0.0.1:8000/ws/bot',
    observationIntervalMs: intEnv('TERRASCOUT_OBSERVATION_INTERVAL_MS', 1000),
  };
}

