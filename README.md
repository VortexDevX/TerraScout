# TerraScout

Autonomous Minecraft terrain intelligence and bot telemetry system.

TerraScout connects a local Java Minecraft bot to a Python backend and React dashboard. It observes the world, logs every decision, moves only when commanded or when autonomy is enabled, and turns live terrain into searchable intelligence: Terrain DNA, PathIQ, BaseRank, WonderHunter, Landmark AI, and Ops Brain diagnostics.

## What It Does

- Connects a Mineflayer TypeScript bot to a local Java Minecraft server.
- Streams typed observations over versioned WebSocket messages.
- Calculates world state, risk, goals, safe movement commands, and terrain reports.
- Keeps bot movement explicit: `Stop`, `Explore`, `Auto`, `Flee`, or one-shot `Move`.
- Stops movement when the watchdog detects stuck pathfinding.
- Persists observations, terrain reports, risk reports, goals, commands, execution results, and decision cycles in SQLite.
- Exports real replay rows for training policy heuristics.
- Shows live telemetry, training summaries, Ops Brain diagnostics, and Terrain Intelligence in the dashboard.

Still intentionally out of scope: crafting, mining, combat AI, food gathering, reinforcement learning, and full map rendering.

## Major Systems

### Terrain Intelligence

The bot samples a 5x5 local terrain probe around its position. Backend turns that probe into:

- Terrain DNA fingerprint
- terrain vector for future similarity search and clustering
- Landmark AI generated region name
- chunk personality
- PathIQ traversal score
- BaseRank settlement score
- WonderHunter terrain-interest score
- biome boundary, mountain, and water feature detections

### Ops Brain

The backend analyzes replay data and exposes `/ops/summary` for:

- stuck movement detection
- distance traveled and recent displacement
- risk histogram
- command success/failure rates
- safety incident counts
- recent failures
- operator recommendations

### Training

Training is based on real replay/debug rows, not fake labels. `python train_bot.py` reads SQLite decision cycles plus execution results and writes a learned policy file under `backend/models/`.

## Quick Start

Real server mode is default. Mock mode is optional and should stay off when you want real Minecraft telemetry.

Backend:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload
```

If your shell is already inside `backend/`, use:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Bot:

```powershell
cd bot
npm install
npm run dev
```

Dashboard:

```powershell
cd dashboard
npm install
npm run dev
```

Open dashboard:

```txt
http://127.0.0.1:5173
```

Optional mock telemetry, only when Minecraft is not running:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/mock/start
Invoke-RestMethod -Method Post http://127.0.0.1:8000/mock/stop
```

Full runbook: [docs/RUNBOOK.md](docs/RUNBOOK.md).

Train policy from real replay outcomes:

```powershell
python train_bot.py
```

## Useful Endpoints

```txt
GET  /health
GET  /telemetry
GET  /ops/summary
GET  /replay/events
GET  /training/summary
GET  /training/examples
GET  /training/export.jsonl
POST /control/start
POST /control/stop
POST /control/move_to
POST /training/feedback
POST /mock/start
POST /mock/stop
WS   /ws/bot
WS   /ws/dashboard
```

## Verification

```powershell
python -m pytest
cd bot
npm run build
npm test
cd ../dashboard
npm run build
npm test
```
