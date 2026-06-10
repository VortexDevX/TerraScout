# TerraScout Runbook

Needed facts and commands for running the full MVP.

## Versions

- Python: 3.12+ recommended. Current local check used Python 3.14.3.
- Node.js: 22+ recommended. Current local check used Node 24.13.0 and npm 11.14.1.
- Backend: FastAPI + Uvicorn.
- Bot: TypeScript + Mineflayer 4.37.1.
- Dashboard: Vite + React + TypeScript.
- Minecraft: Java Edition vanilla local server. Use a server version supported by installed Mineflayer. If auto-detect fails, set `MINECRAFT_VERSION` in `.env` to your exact server version.

## Minecraft Server

MVP assumes local Java server:

```txt
Host: 127.0.0.1
Port: 25565
Mode: vanilla Java
Auth: offline/local test account is easiest for first smoke
```

`server.properties` basics:

```properties
server-port=25565
online-mode=false
enable-command-block=false
pvp=false
difficulty=normal
```

Use `online-mode=true` only after bot auth is configured and tested.

## Environment

Create `.env` from template:

```powershell
Copy-Item .env.example .env
```

Important values:

```env
TERRASCOUT_MOCK_MODE=false
TERRASCOUT_BACKEND_WS=ws://127.0.0.1:8000/ws/bot
MINECRAFT_HOST=127.0.0.1
MINECRAFT_PORT=25565
MINECRAFT_USERNAME=TerraScout
MINECRAFT_VERSION=
TERRASCOUT_OBSERVATION_INTERVAL_MS=1000
TERRASCOUT_DECISION_INTERVAL_MS=1000
TERRASCOUT_DASHBOARD_INTERVAL_MS=1000
```

Leave `MINECRAFT_VERSION` blank for auto-detect. Set it only when Mineflayer cannot detect the server version.

## Install

Backend:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

If your shell is already in `backend/`, same install command works there too:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
cd ..
```

Bot:

```powershell
cd bot
npm install
cd ..
```

Dashboard:

```powershell
cd dashboard
npm install
cd ..
```

## Run Real Mode

Terminal 1, backend:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, dashboard:

```powershell
cd dashboard
npm run dev -- --port 5173
```

Open:

```txt
http://127.0.0.1:5173
```

Terminal 3, bot:

```powershell
cd bot
npm run dev
```

Expected real display:

- dashboard status becomes `bot_connected`
- position updates
- biome updates
- health/hunger updates
- risk and goal update from real observations
- Terrain Intelligence shows local terrain DNA, landmark name, PathIQ, BaseRank, WonderHunter, and probe grid
- `backend/data/terrascout.sqlite3` records replay/debug events

Movement is explicit by default. Use dashboard buttons:

- `Explore`: starts repeated safe explore commands
- `Auto`: lets backend choose simple safe goals
- `Flee`: starts repeated flee commands
- `Stop`: clears queued/in-flight commands and returns to idle
- `Move`: queues one `move_to` command for the X/Y/Z fields

Manual API example:

```powershell
Invoke-RestMethod -Method Post `
  http://127.0.0.1:8000/control/move_to `
  -ContentType "application/json" `
  -Body '{"target":{"x":10,"y":64,"z":10},"max_duration_ms":10000}'
```

## Stop

Stop each terminal with `Ctrl+C`.

If a process gets stuck:

```powershell
Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue
Stop-Process -Id <PID> -Force
```

## Mock Mode

Mock is only for backend/dashboard development without Minecraft. Do not use it for real telemetry.

Start:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/mock/start
```

Stop:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/mock/stop
```

## Verification

Backend:

```powershell
python -m pytest
```

Bot:

```powershell
cd bot
npm run build
npm test
npm audit --audit-level=moderate
```

Dashboard:

```powershell
cd dashboard
npm run build
npm test
npm audit --audit-level=moderate
```

Known audit note: Mineflayer currently pulls auth/protocol dependencies that trigger a moderate `uuid` advisory. npm suggests a force fix that downgrades Mineflayer with breaking changes, so avoid `npm audit fix --force` unless you intentionally retest bot compatibility.

## Replay And Training Data

TerraScout logs every observation, world state, risk report, goal, command, execution result, and combined decision cycle to SQLite.

Useful endpoints:

```txt
GET http://127.0.0.1:8000/replay/events?limit=100
GET http://127.0.0.1:8000/replay/events?event_type=execution_result
GET http://127.0.0.1:8000/ops/summary
GET http://127.0.0.1:8000/training/summary
GET http://127.0.0.1:8000/training/examples?limit=500
GET http://127.0.0.1:8000/training/export.jsonl?limit=1000
POST http://127.0.0.1:8000/training/feedback
```

Save training examples:

```powershell
Invoke-WebRequest `
  "http://127.0.0.1:8000/training/export.jsonl?limit=1000" `
  -OutFile training-export.jsonl
```

Train policy from real replay outcomes:

```powershell
python train_bot.py
```

This writes:

```txt
backend/models/policy.json
```

Default source is `backend/data/terrascout.sqlite3`, so training uses real `decision_cycle` plus `execution_result` rows. JSONL is fallback only.
Restart backend and bot after training so policy changes are picked up.

Current training export is supervised-data prep, not RL. Each row includes:

- features: health, hunger, time, light, hazards, hostile count
- labels: risk score, selected goal, action command
- raw decision cycle for debugging

Collect real data by running backend, dashboard, bot, and Minecraft server, then let the bot explore. Export after a session.

Dashboard training controls:

- Refresh: reloads training summary and latest examples
- Export JSONL: downloads supervised examples from current backend data
- Good/Bad: labels the latest command result as human feedback

Dashboard Ops Brain shows:

- stuck movement detection
- distance traveled and recent displacement
- risk histogram
- command outcome success/failure
- safety incident counts
- recent failures
- operator recommendations

Backend movement watchdog:

- tracks recent positions while a movement command is in flight
- sends `idle` when the bot barely moves across the watchdog window
- records a `movement_watchdog` event in SQLite

## Terrain Intelligence

The bot sends a 5x5 local terrain probe around its current position. Each sample includes:

- surface position
- top block
- biome
- elevation delta
- water/lava flags
- passability flag

Backend converts the probe into:

- Terrain DNA fingerprint
- Terrain vector for future similarity search/clustering
- Landmark AI name
- Chunk personality
- PathIQ traversal score
- BaseRank settlement score
- WonderHunter aesthetics/rarity score
- Biome boundary, mountain, and water features when detected

These are persisted as `terrain_report` events and included in each `decision_cycle`.
