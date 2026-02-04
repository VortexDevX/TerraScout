# ADR 002: Mineflayer Migration

> Architecture Decision Record for migrating from MineRL to Mineflayer + Python Bridge.

---

## 📋 Metadata

| Field          | Value                |
| -------------- | -------------------- |
| **ID**         | ADR-002              |
| **Title**      | Mineflayer Migration |
| **Status**     | ✅ Accepted          |
| **Date**       | 2026-01-XX           |
| **Author**     | VortexDevX           |
| **Supersedes** | ADR-001              |

---

## 🎯 Context

After initial development with MineRL (ADR-001), several limitations became apparent:

1. **MineRL Limitations**
   - Locked to specific Minecraft versions
   - Complex installation with C++ build requirements
   - Limited action space customization
   - No real-time control over bot behavior

2. **Project Requirements**
   - Custom mining patterns (strip mining, branch mining)
   - Fine-grained action control
   - Real-time observation of nearby blocks
   - Integration with live Minecraft servers

---

## ✅ Decision

**Migrate to: Mineflayer + Python Bridge Architecture**

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TERRA SCOUT ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐     HTTP API      ┌─────────────────┐  │
│  │  Python Agent   │ ◄──────────────── │  Mineflayer Bot │  │
│  │  (RL Training)  │ ────────────────► │  (Node.js)      │  │
│  └─────────────────┘     JSON          └────────┬────────┘  │
│         │                                       │           │
│         │                                       ▼           │
│         ▼                              ┌─────────────────┐  │
│  ┌─────────────────┐                   │  Minecraft      │  │
│  │ Stable-Baselines3│                  │  Server         │  │
│  │ PPO Training     │                  └─────────────────┘  │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Rationale

| Aspect            | MineRL                | Mineflayer + Bridge      |
| ----------------- | --------------------- | ------------------------ |
| Action Control    | Fixed action space    | ✅ Fully customizable    |
| Observations      | POV image only        | ✅ Block data, inventory |
| Mining Patterns   | Not supported         | ✅ Custom patterns       |
| Installation      | Complex (C++ build)   | ✅ Simple (npm + pip)    |
| Minecraft Version | Locked to old version | ✅ Latest versions       |
| Real-time Control | Limited               | ✅ Full control          |

---

## 📊 Consequences

### Positive

- ✅ 20 custom actions for mining (strip mine, branch mine, explore cave, etc.)
- ✅ Rich observation space (35 features including Y-level, nearby ores, danger)
- ✅ Works with latest Minecraft (1.21+)
- ✅ Easy to add new actions and observations
- ✅ Can test on live servers

### Negative

- ⚠️ Two runtimes required (Node.js + Python)
- ⚠️ Network latency between components
- ⚠️ No POV image observations (uses computed features instead)

---

## 📎 Related Documents

- [ADR_001_MINERL_SELECTION.md](ADR_001_MINERL_SELECTION.md) - Superseded
- [../TECH_STACK.md](../TECH_STACK.md)
- [../architecture/SYSTEM_OVERVIEW.md](../architecture/SYSTEM_OVERVIEW.md)
