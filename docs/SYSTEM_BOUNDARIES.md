# 🚧 System Boundaries

> Clear definition of what Terra Scout interacts with and what it doesn't.

---

## 🔵 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL WORLD                           │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Kaggle    │    │   GitHub    │    │  Developer  │          │
│  │   (GPU)     │    │   (Code)    │    │  (Human)    │          │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘          │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │                    TERRA SCOUT                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                  Agent Module                       │  │  │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │  │  │
│  │  │  │  Core   │  │ Models  │  │  Utils  │              │  │  │
│  │  │  └─────────┘  └─────────┘  └─────────┘              │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                            │                              │  │
│  │  ┌─────────────────────────▼─────────────────────────────┐│  │
│  │  │               Training Module                         ││  │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                ││  │
│  │  │  │ Scripts │  │ Configs │  │  Logs   │                ││  │
│  │  │  └─────────┘  └─────────┘  └─────────┘                ││  │
│  │  └────────────────────────────────────────────────────────┘│ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 MineRL Environment                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │    │
│  │  │  Minecraft  │  │  Gym API    │  │  Simulator  │      │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🟢 Inside System Boundary

### Components We Control

| Component        | Responsibility                       |
| ---------------- | ------------------------------------ |
| Agent Core       | Decision-making logic                |
| Agent Models     | Neural network architectures         |
| Agent Utils      | Helper functions                     |
| Training Scripts | Training loop execution              |
| Training Configs | Hyperparameters                      |
| Reward Functions | Custom reward design                 |
| Shared Constants | Minecraft constants, action mappings |
| Documentation    | All project docs                     |

### Data We Own

| Data Type           | Location                | Persistence     |
| ------------------- | ----------------------- | --------------- |
| Model Checkpoints   | `training/checkpoints/` | Git LFS / Local |
| Training Logs       | `training/logs/`        | Local           |
| Experiment Results  | `training/experiments/` | Local           |
| Configuration Files | `*/configs/`            | Git             |

---

## 🔴 Outside System Boundary

### External Dependencies

| Dependency        | Type              | Our Control |
| ----------------- | ----------------- | ----------- |
| MineRL            | Environment       | ❌ None     |
| Minecraft         | Game Engine       | ❌ None     |
| PyTorch           | ML Framework      | ❌ None     |
| Stable-Baselines3 | RL Library        | ❌ None     |
| Python            | Runtime           | ❌ None     |
| Kaggle            | Training Platform | ❌ None     |
| GitHub            | Code Hosting      | ❌ None     |

### External Interfaces

| Interface      | Direction       | Data                   |
| -------------- | --------------- | ---------------------- |
| MineRL Gym API | Bidirectional   | Observations ↔ Actions |
| Kaggle API     | Upload/Download | Notebooks, Models      |
| GitHub API     | Push/Pull       | Code                   |
| File System    | Read/Write      | Configs, Logs, Models  |

---

## 🔒 Constraints

### Technical Constraints

| Constraint              | Impact                                             |
| ----------------------- | -------------------------------------------------- |
| MineRL API limitations  | Must work within provided action/observation space |
| Kaggle GPU time limits  | Training sessions must be checkpoint-friendly      |
| Memory constraints      | Model size must fit in available RAM/VRAM          |
| Python 3.10 requirement | All code must be 3.10 compatible                   |

### Environmental Constraints

| Constraint        | Description                             |
| ----------------- | --------------------------------------- |
| Minecraft version | Locked to MineRL-supported version      |
| World generation  | Cannot control world seeds in all cases |
| Tick rate         | Fixed by Minecraft engine               |

### Operational Constraints

| Constraint             | Description                                 |
| ---------------------- | ------------------------------------------- |
| Single agent           | No multi-agent coordination                 |
| No real-time inference | Training/evaluation separate from live play |
| Offline training       | No online learning during evaluation        |

---

## 🔌 Integration Points

### MineRL Integration

```
Terra Scout Agent
       │
       ▼
┌──────────────────┐
│   Gym API        │
│   - reset()      │
│   - step(action) │
│   - render()     │
│   - close()      │
└──────────────────┘
       │
       ▼
MineRL Environment
       │
       ▼
Minecraft Instance
```

### Data Flow Boundaries

| Boundary            | Input                           | Output           |
| ------------------- | ------------------------------- | ---------------- |
| Agent → Environment | Action (int/dict)               | -                |
| Environment → Agent | Observation, Reward, Done, Info | -                |
| Training → Storage  | Model state dict                | Checkpoint files |
| Config → Training   | YAML parameters                 | -                |

---

## 📎 Related Documents

- [PROJECT_SCOPE.md](PROJECT_SCOPE.md)
- [architecture/SYSTEM_OVERVIEW.md](architecture/SYSTEM_OVERVIEW.md)
- [architecture/DATA_FLOW.md](architecture/DATA_FLOW.md)
