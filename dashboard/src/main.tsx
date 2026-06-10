import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity,
  Crosshair,
  Download,
  HeartPulse,
  MapPin,
  Navigation,
  RefreshCw,
  Route,
  ShieldAlert,
  Signal,
  Siren,
  Sparkles,
  Target,
  ThumbsDown,
  ThumbsUp,
} from 'lucide-react';
import type { Envelope, OpsSummary, TelemetrySnapshot, TrainingExample, TrainingSummary } from './types';
import { formatPosition, formatRawPosition } from './format';
import './styles.css';

const wsUrl = import.meta.env.VITE_TERRASCOUT_DASHBOARD_WS ?? 'ws://127.0.0.1:8000/ws/dashboard';
const apiBase = import.meta.env.VITE_TERRASCOUT_API_BASE ?? 'http://127.0.0.1:8000';

function App() {
  const [connected, setConnected] = useState(false);
  const [snapshot, setSnapshot] = useState<TelemetrySnapshot | null>(null);
  const [trainingSummary, setTrainingSummary] = useState<TrainingSummary | null>(null);
  const [trainingExamples, setTrainingExamples] = useState<TrainingExample[]>([]);
  const [trainingStatus, setTrainingStatus] = useState('waiting');
  const [opsSummary, setOpsSummary] = useState<OpsSummary | null>(null);
  const [opsStatus, setOpsStatus] = useState('waiting');
  const [moveTarget, setMoveTarget] = useState({ x: '', y: '', z: '' });
  const [controlStatus, setControlStatus] = useState('ready');

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: number | undefined;
    let closed = false;

    const connect = () => {
      socket = new WebSocket(wsUrl);
      socket.addEventListener('open', () => setConnected(true));
      socket.addEventListener('close', () => {
        setConnected(false);
        if (!closed) reconnectTimer = window.setTimeout(connect, 2000);
      });
      socket.addEventListener('message', (event) => {
        const message = JSON.parse(event.data) as Envelope<TelemetrySnapshot>;
        if (message.type === 'telemetry') setSnapshot(message.payload);
      });
    };

    connect();
    return () => {
      closed = true;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  useEffect(() => {
    refreshOps();
    const timer = window.setInterval(refreshOps, 5000);
    return () => window.clearInterval(timer);
  }, []);

  async function refreshOps() {
    setOpsStatus('refreshing');
    const response = await fetch(`${apiBase}/ops/summary?limit=1000`);
    setOpsSummary((await response.json()) as OpsSummary);
    setOpsStatus('ready');
  }

  async function refreshTraining() {
    setTrainingStatus('refreshing');
    const [summaryResponse, examplesResponse] = await Promise.all([
      fetch(`${apiBase}/training/summary`),
      fetch(`${apiBase}/training/examples?limit=8`),
    ]);
    const summary = (await summaryResponse.json()) as TrainingSummary;
    const examplesBody = (await examplesResponse.json()) as { examples: TrainingExample[] };
    setTrainingSummary(summary);
    setTrainingExamples(examplesBody.examples.slice(-5).reverse());
    setTrainingStatus('ready');
  }

  async function exportTraining() {
    setTrainingStatus('exporting');
    const response = await fetch(`${apiBase}/training/export.jsonl?limit=5000`);
    const text = await response.text();
    const blob = new Blob([text], { type: 'application/x-ndjson' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `terrascout-training-${new Date().toISOString().replace(/[:.]/g, '-')}.jsonl`;
    link.click();
    URL.revokeObjectURL(url);
    setTrainingStatus('exported');
  }

  async function sendFeedback(rating: 'good' | 'bad') {
    const commandId = snapshot?.last_execution_result?.command_id ?? snapshot?.action_command?.command_id ?? null;
    setTrainingStatus(`marking ${rating}`);
    await fetch(`${apiBase}/training/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating,
        command_id: commandId,
        note: snapshot?.last_execution_result?.message ?? snapshot?.action_command?.reason ?? '',
      }),
    });
    await refreshTraining();
  }

  async function startMission(mode: 'auto' | 'explore' | 'flee') {
    setControlStatus(`starting ${mode}`);
    await fetch(`${apiBase}/control/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode }),
    });
    setControlStatus(`${mode} active`);
  }

  async function stopMission() {
    setControlStatus('stopping');
    await fetch(`${apiBase}/control/stop`, { method: 'POST' });
    setControlStatus('stopped');
  }

  function useCurrentPosition() {
    const position = snapshot?.observation?.position;
    if (!position) return;
    setMoveTarget({
      x: String(Math.round(position.x)),
      y: String(Math.round(position.y)),
      z: String(Math.round(position.z)),
    });
  }

  async function moveToTarget() {
    const x = Number(moveTarget.x);
    const y = Number(moveTarget.y);
    const z = Number(moveTarget.z);
    if (![x, y, z].every(Number.isFinite)) {
      setControlStatus('bad target');
      return;
    }
    setControlStatus('queueing move');
    await fetch(`${apiBase}/control/move_to`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: { x, y, z }, max_duration_ms: 10000 }),
    });
    setControlStatus('move queued');
  }

  const events = useMemo(() => snapshot?.recent_events.slice(-8).reverse() ?? [], [snapshot]);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <h1>TerraScout</h1>
          <p>Autonomous Minecraft research telemetry</p>
        </div>
        <div className={`status ${connected ? 'online' : 'offline'}`}>
          <Signal size={18} />
          <span>{connected ? snapshot?.connection_status ?? 'connected' : 'dashboard offline'}</span>
        </div>
        <div className="toolbar">
          <button type="button" title="Start explore mission" onClick={() => startMission('explore')}>
            Explore
          </button>
          <button type="button" title="Start automatic mission" onClick={() => startMission('auto')}>
            Auto
          </button>
          <button type="button" title="Start flee mission" onClick={() => startMission('flee')}>
            Flee
          </button>
          <button type="button" title="Stop bot autonomy" onClick={stopMission}>
            Stop
          </button>
        </div>
      </header>

      <section className="metrics">
        <Metric icon={<MapPin />} label="Position" value={formatPosition(snapshot)} />
        <Metric icon={<Activity />} label="Biome" value={snapshot?.observation?.biome ?? 'unknown'} />
        <Metric
          icon={<HeartPulse />}
          label="Health / Hunger"
          value={`${snapshot?.observation?.health ?? '-'} / ${snapshot?.observation?.hunger ?? '-'}`}
        />
        <Metric icon={<Target />} label="Goal" value={snapshot?.selected_goal?.name ?? 'none'} />
        <Metric icon={<ShieldAlert />} label="Risk" value={`${snapshot?.risk_report?.score ?? 0}/100`} />
        <Metric icon={<Signal />} label="Autonomy" value={snapshot?.autonomy_enabled ? 'on' : 'off'} />
        <Metric icon={<Target />} label="Mission" value={snapshot?.mission_mode ?? 'idle'} />
        <Metric icon={<Siren />} label="Stuck" value={opsSummary?.stuck.is_stuck ? 'yes' : 'no'} />
      </section>

      <section className="terrain-grid">
        <div className="panel terrain-panel">
          <div className="panel-head">
            <h2>Terrain Intelligence</h2>
            <div className="status subtle">
              <Sparkles size={16} />
              <span>{snapshot?.terrain_report?.personality ?? 'unknown'}</span>
            </div>
          </div>
          <div className="terrain-hero">
            <span>Landmark AI</span>
            <strong>{snapshot?.terrain_report?.landmark_name ?? 'Unscouted Region'}</strong>
            <code>{snapshot?.terrain_report?.fingerprint ?? 'no-dna'}</code>
          </div>
          <div className="summary">
            <MetricText label="BaseRank" value={`${snapshot?.terrain_report?.base_score ?? 0}`} />
            <MetricText label="WonderHunter" value={`${snapshot?.terrain_report?.wonder_score ?? 0}`} />
            <MetricText label="PathIQ" value={`${snapshot?.terrain_report?.path_iq ?? 0}`} />
            <MetricText label="Samples" value={`${snapshot?.terrain_report?.sample_count ?? 0}`} />
          </div>
          <div className="mini-columns">
            <TerrainScalar label="Relief" value={snapshot?.terrain_report?.elevation_range ?? 0} />
            <TerrainScalar label="Ruggedness" value={snapshot?.terrain_report?.ruggedness ?? 0} />
            <TerrainScalar label="Water" value={(snapshot?.terrain_report?.water_ratio ?? 0) * 100} suffix="%" />
          </div>
        </div>

        <div className="panel terrain-panel">
          <h2>Terrain Features</h2>
          <div className="log">
            {(snapshot?.terrain_report?.features ?? []).map((feature) => (
              <div className="logline" key={feature.name}>
                <span>{feature.name}</span>
                <strong>{feature.score}</strong>
              </div>
            ))}
            {!snapshot?.terrain_report?.features.length && <p className="empty">Waiting for terrain samples.</p>}
          </div>
          <h2 className="subhead">Terrain DNA Vector</h2>
          <div className="dna-vector">
            {(snapshot?.terrain_report?.terrain_vector ?? []).map((value, index) => (
              <span key={index} title={`v${index}: ${value}`}>
                {value.toFixed(value >= 10 ? 0 : 2)}
              </span>
            ))}
          </div>
        </div>

        <div className="panel terrain-panel">
          <h2>Local Probe</h2>
          <div className="probe-grid">
            {(snapshot?.observation?.terrain_samples ?? []).slice(0, 25).map((sample, index) => (
              <span
                className={`probe-cell ${sample.is_lava ? 'danger' : sample.is_water ? 'water' : sample.is_passable ? 'passable' : 'blocked'}`}
                key={`${sample.position.x}-${sample.position.z}-${index}`}
                title={`${sample.top_block} ${sample.elevation_delta >= 0 ? '+' : ''}${sample.elevation_delta}`}
              />
            ))}
          </div>
          <div className="list">
            <div className="row">
              <span>chunk</span>
              <strong>{snapshot?.terrain_report?.chunk_key ?? 'unknown'}</strong>
            </div>
            <div className="row">
              <span>passable</span>
              <strong>{((snapshot?.terrain_report?.passable_ratio ?? 0) * 100).toFixed(0)}%</strong>
            </div>
            <div className="row">
              <span>route mode</span>
              <strong className="icon-text">
                <Route size={14} /> {routeMode(snapshot?.terrain_report?.path_iq ?? 0)}
              </strong>
            </div>
          </div>
        </div>
      </section>

      <section className="details">
        <div className="panel">
          <h2>Risk Sources</h2>
          <div className="list">
            {(snapshot?.risk_report?.sources.length ? snapshot.risk_report.sources : []).map((source) => (
              <div className="row" key={source.name}>
                <span>{source.name}</span>
                <strong>{source.score}</strong>
              </div>
            ))}
            {!snapshot?.risk_report?.sources.length && <p className="empty">No active risk sources.</p>}
          </div>
        </div>

        <div className="panel">
          <h2>Command</h2>
          <div className="list">
            <div className="row">
              <span>current</span>
              <strong>{snapshot?.action_command?.command ?? 'none'}</strong>
            </div>
            <div className="row">
              <span>reason</span>
              <strong>{snapshot?.action_command?.reason ?? 'waiting'}</strong>
            </div>
            <div className="row">
              <span>radius</span>
              <strong>{snapshot?.action_command?.radius ?? 'none'}</strong>
            </div>
            <div className="row">
              <span>in flight</span>
              <strong>{snapshot?.command_in_flight?.command_id ?? 'none'}</strong>
            </div>
            <div className="row">
              <span>queued</span>
              <strong>{snapshot?.queued_command?.command_id ?? 'none'}</strong>
            </div>
            <div className="row">
              <span>last result</span>
              <strong>{snapshot?.last_execution_result?.ok === false ? 'failed' : 'ok'}</strong>
            </div>
            <div className="row">
              <span>message</span>
              <strong>{snapshot?.last_execution_result?.message ?? 'none'}</strong>
            </div>
            <div className="row">
              <span>light / time</span>
              <strong>
                {snapshot?.observation
                  ? `${snapshot.observation.light_level} / ${snapshot.observation.time_of_day}`
                  : 'unknown'}
              </strong>
            </div>
            <div className="row">
              <span>feet / floor</span>
              <strong>
                {snapshot?.observation
                  ? `${snapshot.observation.feet_block ?? 'unknown'} / ${
                      snapshot.observation.floor_block ?? 'unknown'
                    }`
                  : 'unknown'}
              </strong>
            </div>
          </div>
        </div>

        <div className="panel">
          <h2>Recent Events</h2>
          <div className="log">
            {events.map((event) => (
              <div className="logline" key={event.id}>
                <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
                <strong>{event.event_type}</strong>
              </div>
            ))}
            {!events.length && <p className="empty">Waiting for telemetry.</p>}
          </div>
        </div>

        <div className="panel">
          <h2>Manual Control</h2>
          <div className="control-grid">
            <button type="button" title="Use current position" onClick={useCurrentPosition}>
              <Crosshair size={16} />
              <span>Use Current</span>
            </button>
            <button type="button" title="Queue one movement command" onClick={moveToTarget}>
              <Navigation size={16} />
              <span>Move</span>
            </button>
          </div>
          <div className="manual-form">
            {(['x', 'y', 'z'] as const).map((axis) => (
              <label key={axis}>
                <span>{axis.toUpperCase()}</span>
                <input
                  inputMode="decimal"
                  value={moveTarget[axis]}
                  onChange={(event) => setMoveTarget((current) => ({ ...current, [axis]: event.target.value }))}
                />
              </label>
            ))}
          </div>
          <div className="list">
            <div className="row">
              <span>control</span>
              <strong>{controlStatus}</strong>
            </div>
            <div className="row">
              <span>queued target</span>
              <strong>{formatRawPosition(snapshot?.queued_command?.target)}</strong>
            </div>
            <div className="row">
              <span>last position</span>
              <strong>{formatRawPosition(snapshot?.last_execution_result?.position)}</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="training-grid">
        <div className="panel training-panel">
          <div className="panel-head">
            <h2>Training</h2>
            <div className="toolbar">
              <button type="button" title="Refresh training data" onClick={refreshTraining}>
                <RefreshCw size={16} />
              </button>
              <button type="button" title="Export JSONL" onClick={exportTraining}>
                <Download size={16} />
              </button>
              <button type="button" title="Mark latest command good" onClick={() => sendFeedback('good')}>
                <ThumbsUp size={16} />
              </button>
              <button type="button" title="Mark latest command bad" onClick={() => sendFeedback('bad')}>
                <ThumbsDown size={16} />
              </button>
            </div>
          </div>
          <div className="summary">
            <MetricText label="Examples" value={`${trainingSummary?.training_examples ?? 0}`} />
            <MetricText label="Avg Risk" value={`${trainingSummary?.average_risk_score ?? 0}`} />
            <MetricText label="Max Risk" value={`${trainingSummary?.max_risk_score ?? 0}`} />
            <MetricText label="Status" value={trainingStatus} />
          </div>
          <div className="mini-columns">
            <CountList title="Goals" counts={trainingSummary?.goal_counts ?? {}} />
            <CountList title="Commands" counts={trainingSummary?.command_counts ?? {}} />
            <CountList title="Events" counts={trainingSummary?.event_counts ?? {}} />
          </div>
        </div>

        <div className="panel examples-panel">
          <h2>Latest Training Examples</h2>
          <div className="examples">
            {trainingExamples.map((example) => (
              <div className="example" key={example.event_id}>
                <span>{new Date(example.timestamp).toLocaleTimeString()}</span>
                <strong>{example.labels.goal}</strong>
                <strong>{example.labels.command}</strong>
                <span>risk {example.labels.risk_score}</span>
              </div>
            ))}
            {!trainingExamples.length && <p className="empty">Refresh training data to inspect examples.</p>}
          </div>
        </div>
      </section>

      <section className="ops-grid">
        <div className="panel ops-panel">
          <div className="panel-head">
            <h2>Ops Brain</h2>
            <div className="toolbar">
              <button type="button" title="Refresh ops analysis" onClick={refreshOps}>
                <RefreshCw size={16} />
              </button>
            </div>
          </div>
          <div className="summary ops-summary">
            <MetricText label="Status" value={opsStatus} />
            <MetricText label="Distance" value={`${opsSummary?.distance_traveled ?? 0}`} />
            <MetricText label="Recent Move" value={`${opsSummary?.recent_displacement ?? 0}`} />
            <MetricText label="Risk Avg/Max" value={`${opsSummary?.risk.average ?? 0} / ${opsSummary?.risk.max ?? 0}`} />
          </div>
          <div className="mini-columns">
            <CountList title="Risk Buckets" counts={opsSummary?.risk.histogram ?? {}} />
            <CountList title="Safety Incidents" counts={opsSummary?.safety_incidents ?? {}} />
            <CommandStats counts={opsSummary?.command_stats ?? {}} />
          </div>
        </div>

        <div className="panel ops-panel">
          <h2>Recommendations</h2>
          <div className="log">
            {(opsSummary?.recommendations ?? []).map((recommendation) => (
              <div className="logline textline" key={recommendation}>
                <strong>{recommendation}</strong>
              </div>
            ))}
            {!opsSummary?.recommendations.length && <p className="empty">Waiting for ops data.</p>}
          </div>
          <h2 className="subhead">Recent Failures</h2>
          <div className="log">
            {(opsSummary?.recent_failures ?? []).map((failure) => (
              <div className="logline textline" key={`${failure.command_id}-${failure.timestamp}`}>
                <span>{failure.command}</span>
                <strong>{failure.message}</strong>
              </div>
            ))}
            {!opsSummary?.recent_failures.length && <p className="empty">No recent failures.</p>}
          </div>
        </div>
      </section>
    </main>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="metric">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MetricText({ label, value }: { label: string; value: string }) {
  return (
    <div className="summary-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function TerrainScalar({ label, value, suffix = '' }: { label: string; value: number; suffix?: string }) {
  return (
    <div className="terrain-scalar">
      <span>{label}</span>
      <strong>
        {value.toFixed(value >= 10 ? 0 : 1)}
        {suffix}
      </strong>
    </div>
  );
}

function routeMode(pathIq: number): string {
  if (pathIq >= 75) return 'fast';
  if (pathIq >= 45) return 'careful';
  return 'hostile';
}

function CountList({ title, counts }: { title: string; counts: Record<string, number> }) {
  const entries = Object.entries(counts).slice(0, 6);
  return (
    <div className="count-list">
      <h3>{title}</h3>
      {entries.map(([name, count]) => (
        <div className="row compact" key={name}>
          <span>{name}</span>
          <strong>{count}</strong>
        </div>
      ))}
      {!entries.length && <p className="empty small">No data.</p>}
    </div>
  );
}

function CommandStats({ counts }: { counts: OpsSummary['command_stats'] }) {
  const entries = Object.entries(counts).slice(0, 6);
  return (
    <div className="count-list">
      <h3>Command Outcomes</h3>
      {entries.map(([name, stats]) => (
        <div className="row compact" key={name}>
          <span>{name}</span>
          <strong>
            {stats.ok}/{stats.failed} {(stats.success_rate * 100).toFixed(0)}%
          </strong>
        </div>
      ))}
      {!entries.length && <p className="empty small">No data.</p>}
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
