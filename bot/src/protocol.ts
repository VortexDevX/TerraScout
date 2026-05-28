export const PROTOCOL_VERSION = '1';

export type Position = {
  x: number;
  y: number;
  z: number;
};

export type HostileMob = {
  kind: string;
  position: Position;
  distance: number;
};

export type Observation = {
  bot_id: string;
  position: Position;
  biome: string;
  health: number;
  hunger: number;
  time_of_day: number;
  light_level: number;
  nearby_hostiles: HostileMob[];
  nearby_lava: boolean;
  nearby_cliff: boolean;
  nearby_deep_water: boolean;
  pathfinding_error?: string | null;
};

export type CommandType = 'idle' | 'explore' | 'flee' | 'move_to' | 'report_state';

export type ActionCommand = {
  command_id: string;
  command: CommandType;
  reason: string;
  target?: Position | null;
  max_duration_ms: number;
};

export type ExecutionResult = {
  command_id: string;
  ok: boolean;
  message: string;
  position?: Position | null;
};

export type Envelope<T> = {
  type: string;
  timestamp: string;
  protocol_version: string;
  payload: T;
};

export function envelope<T>(type: string, payload: T): Envelope<T> {
  return {
    type,
    timestamp: new Date().toISOString(),
    protocol_version: PROTOCOL_VERSION,
    payload,
  };
}

