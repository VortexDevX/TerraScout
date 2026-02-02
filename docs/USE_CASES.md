# 🎯 Use Cases

> Detailed use case specifications for Terra Scout.

---

## 📋 Use Case Overview

| ID    | Name                  | Priority | Status     |
| ----- | --------------------- | -------- | ---------- |
| UC-01 | Train Agent           | P0       | 🔄 Planned |
| UC-02 | Evaluate Agent        | P0       | 🔄 Planned |
| UC-03 | Find Diamond          | P0       | 🔄 Planned |
| UC-04 | Resume Training       | P1       | 🔄 Planned |
| UC-05 | Export Model          | P1       | 🔄 Planned |
| UC-06 | View Training Metrics | P2       | 🔄 Planned |

---

## UC-01: Train Agent

### Description

Developer initiates training of the Terra Scout agent on MineRL environment.

### Actors

- **Primary:** Developer
- **Secondary:** Kaggle Platform

### Preconditions

1. MineRL environment is installed and functional
2. Training configuration is defined
3. GPU resources are available (Kaggle)

### Main Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│Developer │     │Training      │     │ MineRL      │     │ Kaggle   │
│          │     │Script        │     │ Environment │     │ GPU      │
└────┬─────┘     └──────┬───────┘     └──────┬──────┘     └────┬─────┘
     │                  │                    │                 │
     │ 1. Start train   │                    │                 │
     │─────────────────>│                    │                 │
     │                  │                    │                 │
     │                  │ 2. Load config     │                 │
     │                  │───────────────────>│                 │
     │                  │                    │                 │
     │                  │ 3. Initialize env  │                 │
     │                  │<───────────────────│                 │
     │                  │                    │                 │
     │                  │ 4. Training loop   │                 │
     │                  │═══════════════════>│                 │
     │                  │    (episodes)      │<───────────────>│
     │                  │<═══════════════════│                 │
     │                  │                    │                 │
     │                  │ 5. Save checkpoint │                 │
     │                  │────────────────────────────────────> │
     │                  │                    │                 │
     │ 6. Training done │                    │                 │
     │<─────────────────│                    │                 │
     │                  │                    │                 │
```

### Postconditions

1. Model checkpoint saved
2. Training logs recorded
3. Metrics available for review

### Alternative Flows

- **A1:** Training interrupted → Resume from last checkpoint
- **A2:** Out of memory → Reduce batch size, retry

---

## UC-02: Evaluate Agent

### Description

Developer evaluates trained agent's performance on test episodes.

### Actors

- **Primary:** Developer

### Preconditions

1. Trained model checkpoint exists
2. MineRL environment available

### Main Flow

```
Developer               Evaluate Script          MineRL Environment
    │                        │                          │
    │ 1. Run evaluation      │                          │
    │───────────────────────>│                          │
    │                        │                          │
    │                        │ 2. Load model            │
    │                        │─────────────────────────>│
    │                        │                          │
    │                        │ 3. Run N episodes        │
    │                        │═════════════════════════>│
    │                        │<═════════════════════════│
    │                        │                          │
    │                        │ 4. Compute metrics       │
    │                        │──────────┐               │
    │                        │<─────────┘               │
    │                        │                          │
    │ 5. Return results      │                          │
    │<───────────────────────│                          │
    │                        │                          │
```

### Postconditions

1. Evaluation metrics computed
2. Results saved/displayed

### Metrics Computed

- Diamond found rate
- Average steps to diamond
- Survival rate
- Average reward per episode

---

## UC-03: Find Diamond (Agent Behavior)

### Description

The agent autonomously explores and locates diamond ore.

### Actors

- **Primary:** Terra Scout Agent
- **Secondary:** MineRL Environment

### Preconditions

1. Agent is initialized in Minecraft world
2. Agent has trained policy loaded

### Main Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT BEHAVIOR LOOP                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │ Observe  │───>│ Process  │───>│ Decide   │───>│ Execute  │   │
│  │ State    │    │ State    │    │ Action   │    │ Action   │   │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│       ▲                                               │         │
│       │                                               │         │
│       └───────────────────────────────────────────────┘         │
│                         (repeat)                                │
│                                                                 │
│  TERMINATION CONDITIONS:                                        │
│  ├── Diamond found ✅                                           │
│  ├── Agent died ❌                                              │
│  └── Max steps reached ⏱️                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Decision Flow

```
                    ┌─────────────────┐
                    │ Current State   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Policy Network  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  Move    │  │  Mine    │  │  Look    │
        │ Forward  │  │  Block   │  │  Around  │
        └──────────┘  └──────────┘  └──────────┘
```

### Postconditions

- Episode ends with success (diamond) or failure (death/timeout)
- Experience stored for potential learning

---

## UC-04: Resume Training

### Description

Developer resumes training from a saved checkpoint.

### Preconditions

1. Valid checkpoint file exists
2. Checkpoint is compatible with current code

### Main Flow

1. Developer specifies checkpoint path
2. Training script loads model state
3. Training script loads optimizer state
4. Training continues from saved step

### Postconditions

- Training continues without loss of progress

---

## UC-05: Export Model

### Description

Developer exports trained model for deployment or sharing.

### Preconditions

1. Trained model exists
2. Export format specified

### Main Flow

1. Developer runs export script
2. Script loads best checkpoint
3. Script saves model in portable format
4. Script generates model metadata

### Output Formats

- PyTorch (.pt)
- ONNX (.onnx) - optional
- Stable-Baselines3 (.zip)

---

## UC-06: View Training Metrics

### Description

Developer views training progress and metrics.

### Preconditions

1. Training has generated logs
2. TensorBoard or logging system active

### Main Flow

1. Developer launches TensorBoard
2. Developer selects experiment run
3. Metrics displayed graphically

### Metrics Available

- Episode reward (mean, min, max)
- Episode length
- Loss values
- Learning rate
- Diamond discovery rate

---

## 📎 Related Documents

- [PROJECT_SCOPE.md](PROJECT_SCOPE.md)
- [architecture/DATA_FLOW.md](architecture/DATA_FLOW.md)
