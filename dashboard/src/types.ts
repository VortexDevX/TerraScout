export type Position = {
  x: number;
  y: number;
  z: number;
};

export type Observation = {
  bot_id: string;
  position: Position;
  biome: string;
  health: number;
  hunger: number;
  time_of_day: number;
  light_level: number;
  feet_block?: string | null;
  floor_block?: string | null;
  terrain_samples?: TerrainSample[];
};

export type TerrainSample = {
  position: Position;
  top_block: string;
  biome: string;
  elevation_delta: number;
  is_water: boolean;
  is_lava: boolean;
  is_passable: boolean;
};

export type RiskReport = {
  score: number;
  sources: { name: string; score: number; detail: string }[];
};

export type TerrainReport = {
  chunk_key: string;
  fingerprint: string;
  sample_count: number;
  elevation_range: number;
  ruggedness: number;
  water_ratio: number;
  lava_ratio: number;
  passable_ratio: number;
  path_iq: number;
  base_score: number;
  wonder_score: number;
  personality: string;
  landmark_name: string;
  terrain_vector: number[];
  features: { name: string; score: number; detail: string }[];
};

export type SelectedGoal = {
  name: string;
  utility: number;
  reason: string;
};

export type ActionCommand = {
  command_id: string;
  command: string;
  reason: string;
  target?: Position | null;
  radius?: number | null;
  max_duration_ms?: number;
};

export type ExecutionResult = {
  command_id: string;
  ok: boolean;
  message: string;
  position?: Position | null;
};

export type TelemetrySnapshot = {
  connection_status: 'offline' | 'bot_connected' | 'mock_connected';
  autonomy_enabled: boolean;
  mission_mode: 'idle' | 'manual' | 'auto' | 'explore' | 'flee';
  command_in_flight: ActionCommand | null;
  queued_command: ActionCommand | null;
  observation: Observation | null;
  risk_report: RiskReport | null;
  terrain_report: TerrainReport | null;
  selected_goal: SelectedGoal | null;
  action_command: ActionCommand | null;
  last_execution_result: ExecutionResult | null;
  recent_events: { id: number; timestamp: string; event_type: string; payload: unknown }[];
};

export type Envelope<T> = {
  type: string;
  timestamp: string;
  protocol_version: string;
  payload: T;
};

export type TrainingSummary = {
  training_examples: number;
  event_counts: Record<string, number>;
  goal_counts: Record<string, number>;
  command_counts: Record<string, number>;
  average_risk_score: number;
  max_risk_score: number;
};

export type TrainingExample = {
  event_id: number;
  timestamp: string;
  features: Record<string, number | string | null>;
  labels: {
    risk_score: number;
    goal: string;
    command: string;
  };
};

export type OpsSummary = {
  event_count: number;
  observation_count: number;
  decision_count: number;
  execution_count: number;
  latest_position: Position | null;
  distance_traveled: number;
  recent_displacement: number;
  stuck: {
    is_stuck: boolean;
    movement_without_result: boolean;
    window_observations: number;
    reason: string;
  };
  risk: {
    average: number;
    max: number;
    histogram: Record<string, number>;
  };
  command_stats: Record<string, { ok: number; failed: number; success_rate: number }>;
  safety_incidents: Record<string, number>;
  recent_failures: { timestamp: string; command_id: string; command: string; message: string }[];
  recommendations: string[];
};
