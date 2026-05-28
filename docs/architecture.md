# TerraScout MVP Architecture

```txt
Minecraft Java Server
        |
Mineflayer TypeScript Bot
        |
WebSocket: /ws/bot
        |
FastAPI Backend
  - world state builder
  - risk analyzer
  - goal selector
  - command planner
  - SQLite replay log
        |
WebSocket: /ws/dashboard
        |
React Dashboard
```

## Protocol

All WebSocket messages use an envelope:

```json
{
  "type": "observation",
  "timestamp": "2026-05-28T12:00:00Z",
  "protocol_version": "1",
  "payload": {}
}
```

Initial command types:

- `idle`
- `explore`
- `flee`
- `move_to`
- `report_state`

## Safe Movement

Safe movement for MVP means:

- avoid cliffs
- avoid lava
- avoid hostile mobs
- avoid deep water unless required
- stop movement and report error if pathfinding fails

