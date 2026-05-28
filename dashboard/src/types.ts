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
};

export type RiskReport = {
  score: number;
  sources: { name: string; score: number; detail: string }[];
};

export type SelectedGoal = {
  name: string;
  utility: number;
  reason: string;
};

export type TelemetrySnapshot = {
  connection_status: 'offline' | 'bot_connected' | 'mock_connected';
  observation: Observation | null;
  risk_report: RiskReport | null;
  selected_goal: SelectedGoal | null;
  recent_events: { id: number; timestamp: string; event_type: string; payload: unknown }[];
};

export type Envelope<T> = {
  type: string;
  timestamp: string;
  protocol_version: string;
  payload: T;
};

