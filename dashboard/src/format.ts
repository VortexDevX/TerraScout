import type { Position, TelemetrySnapshot } from './types';

export function formatPosition(snapshot: TelemetrySnapshot | null): string {
  const position = snapshot?.observation?.position;
  return formatRawPosition(position);
}

export function formatRawPosition(position: Position | null | undefined): string {
  if (!position) return 'unknown';
  return `${position.x.toFixed(1)}, ${position.y.toFixed(1)}, ${position.z.toFixed(1)}`;
}
