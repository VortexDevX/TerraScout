# TerraScout

Autonomous Minecraft environmental intelligence MVP.

## MVP Scope

- Local Java Minecraft server connection through a Mineflayer TypeScript bot.
- Python FastAPI backend for observations, risk, goals, commands, and replay logs.
- Minimal React dashboard for live telemetry.
- Mock observation mode so backend and dashboard run without Minecraft.

Out of scope for MVP: crafting, mining, combat AI, food gathering, map UI, heatmaps, RL.

## Quick Start

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --reload
```

Start mock telemetry:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/mock/start
```

Dashboard:

```powershell
cd dashboard
npm install
npm run dev
```

Bot:

```powershell
cd bot
npm install
npm run dev
```

