# 🤖 Terra Scout Bot

> Mineflayer-based Minecraft bot for Terra Scout.

## 📁 Structure

```
bot/
├── src/
│   ├── index.js          # Main entry point
│   ├── bot.js            # Bot logic
│   ├── server.js         # HTTP/WebSocket API
│   ├── actions/          # Action handlers
│   │   ├── movement.js
│   │   ├── mining.js
│   │   └── combat.js
│   ├── observers/        # State observers
│   │   ├── state.js
│   │   ├── inventory.js
│   │   └── world.js
│   └── utils/
│       ├── logger.js
│       └── config.js
├── package.json
└── .env
```

## 🚀 Quick Start

### Start Minecraft Server First

```powershell
cd ../server
./start.ps1
```

### Start Bot

```powershell
npm start
```

### Development Mode (auto-restart)

```powershell
npm run dev
```

## 🔌 API Endpoints

| Endpoint       | Method | Description         |
| -------------- | ------ | ------------------- |
| `/status`      | GET    | Bot status          |
| `/observation` | GET    | Current observation |
| `/action`      | POST   | Execute action      |
| `/reset`       | POST   | Reset episode       |

## 📡 WebSocket Events

| Event         | Direction       | Description    |
| ------------- | --------------- | -------------- |
| `observation` | Server → Client | State update   |
| `action`      | Client → Server | Action command |
| `reward`      | Server → Client | Reward signal  |
| `done`        | Server → Client | Episode end    |
