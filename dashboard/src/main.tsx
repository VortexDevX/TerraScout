import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, HeartPulse, MapPin, ShieldAlert, Signal, Target } from 'lucide-react';
import type { Envelope, TelemetrySnapshot } from './types';
import { formatPosition } from './format';
import './styles.css';

const wsUrl = import.meta.env.VITE_TERRASCOUT_DASHBOARD_WS ?? 'ws://127.0.0.1:8000/ws/dashboard';

function App() {
  const [connected, setConnected] = useState(false);
  const [snapshot, setSnapshot] = useState<TelemetrySnapshot | null>(null);

  useEffect(() => {
    const socket = new WebSocket(wsUrl);
    socket.addEventListener('open', () => setConnected(true));
    socket.addEventListener('close', () => setConnected(false));
    socket.addEventListener('message', (event) => {
      const message = JSON.parse(event.data) as Envelope<TelemetrySnapshot>;
      if (message.type === 'telemetry') setSnapshot(message.payload);
    });
    return () => socket.close();
  }, []);

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

createRoot(document.getElementById('root')!).render(<App />);
