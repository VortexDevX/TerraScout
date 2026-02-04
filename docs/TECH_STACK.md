# 🛠️ Technology Stack

> Complete list of technologies, tools, and dependencies used in Terra Scout.

---

## 📊 Stack Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      TERRA SCOUT STACK                      │
├─────────────────────────────────────────────────────────────┤
│  TRAINING PLATFORM                                          │
│  └── Local (GPU: RTX) / Kaggle (T4/P100)                    │
├─────────────────────────────────────────────────────────────┤
│  REINFORCEMENT LEARNING                                     │
│  ├── Stable-Baselines3 (PPO algorithm)                      │
│  └── Gymnasium (Environment API)                            │
├─────────────────────────────────────────────────────────────┤
│  DEEP LEARNING                                              │
│  └── PyTorch (Neural networks)                              │
├─────────────────────────────────────────────────────────────┤
│  BRIDGE LAYER (Python ↔ Node.js)                            │
│  ├── HTTP API (Express.js server)                           │
│  └── BridgeClient (Python requests)                         │
├─────────────────────────────────────────────────────────────┤
│  MINECRAFT BOT (Node.js)                                    │
│  ├── Mineflayer (Bot framework)                             │
│  └── mineflayer-pathfinder (Navigation)                     │
├─────────────────────────────────────────────────────────────┤
│  ENVIRONMENT                                                │
│  ├── Minecraft Java Edition Server                          │
│  └── PaperMC (Server software)                              │
├─────────────────────────────────────────────────────────────┤
│  LANGUAGE & RUNTIME                                         │
│  ├── Python 3.10 (Agent & Training)                         │
│  └── Node.js 22.x (Bot)                                     │
├─────────────────────────────────────────────────────────────┤
│  DEVELOPMENT TOOLS                                          │
│  ├── Git / GitHub                                           │
│  ├── VS Code                                                │
│  └── PowerShell                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐍 Python Dependencies

### Core Dependencies

| Package             | Version | Purpose                  |
| ------------------- | ------- | ------------------------ |
| `gymnasium`         | 0.29.x  | Environment API standard |
| `stable-baselines3` | 2.x     | RL algorithms (PPO)      |
| `torch`             | 2.x     | Neural network framework |
| `numpy`             | 1.24.x  | Numerical computing      |
| `requests`          | 2.x     | HTTP client for bridge   |

### Utility Dependencies

| Package         | Version | Purpose                |
| --------------- | ------- | ---------------------- |
| `opencv-python` | 4.x     | Image processing       |
| `pillow`        | 10.x    | Image handling         |
| `pyyaml`        | 6.x     | Config file parsing    |
| `tqdm`          | 4.x     | Progress bars          |
| `tensorboard`   | 2.x     | Training visualization |
| `matplotlib`    | 3.x     | Plotting               |
| `rich`          | 13.x    | Console formatting     |

### Development Dependencies

| Package      | Version | Purpose            |
| ------------ | ------- | ------------------ |
| `pytest`     | 7.x     | Testing framework  |
| `pytest-cov` | 4.x     | Coverage reporting |
| `black`      | 23.x    | Code formatting    |
| `isort`      | 5.x     | Import sorting     |
| `flake8`     | 6.x     | Linting            |
| `mypy`       | 1.x     | Type checking      |

---

## 📦 Node.js Dependencies

### Bot Core

| Package                 | Version | Purpose                    |
| ----------------------- | ------- | -------------------------- |
| `mineflayer`            | 4.x     | Minecraft bot framework    |
| `mineflayer-pathfinder` | 2.x     | Navigation and pathfinding |
| `express`               | 4.x     | HTTP server for bridge     |
| `cors`                  | 2.x     | Cross-origin requests      |

### Minecraft Server

| Component | Version | Notes                            |
| --------- | ------- | -------------------------------- |
| Java      | 21+     | Required by Minecraft server     |
| PaperMC   | 1.21.x  | High-performance server software |

---

## 🎮 Bot Environment

### Custom Gymnasium Environment

Terra Scout uses a custom Gymnasium environment that bridges to the Mineflayer bot:

| Environment     | Description                              |
| --------------- | ---------------------------------------- |
| `TerraScout-v0` | Basic environment with bridge connection |
| `TerraScout-v2` | Enhanced observations and rewards        |

### Observation Space

| Component               | Type  | Shape       |
| ----------------------- | ----- | ----------- |
| POV (First-person view) | Image | (64, 64, 3) |
| Inventory               | Dict  | Variable    |
| Equipped Items          | Dict  | Variable    |
| Compass                 | Dict  | Variable    |

### Action Space

| Action  | Type     | Description                 |
| ------- | -------- | --------------------------- |
| camera  | Box      | Mouse movement (pitch, yaw) |
| forward | Discrete | Move forward                |
| back    | Discrete | Move backward               |
| left    | Discrete | Strafe left                 |
| right   | Discrete | Strafe right                |
| jump    | Discrete | Jump                        |
| sneak   | Discrete | Sneak                       |
| sprint  | Discrete | Sprint                      |
| attack  | Discrete | Attack/mine                 |

---

## 🖥️ Hardware Requirements

### Local Development

| Component | Minimum      | Recommended   |
| --------- | ------------ | ------------- |
| CPU       | 4 cores      | 8 cores       |
| RAM       | 8 GB         | 16 GB         |
| GPU       | Not required | NVIDIA (CUDA) |
| Storage   | 20 GB        | 50 GB         |

### Kaggle Training

| Resource     | Allocation   |
| ------------ | ------------ |
| GPU          | T4 or P100   |
| RAM          | 13-16 GB     |
| Disk         | 20 GB        |
| Session Time | 12 hours max |

---

## 📁 File Formats

| Type              | Format       | Usage                     |
| ----------------- | ------------ | ------------------------- |
| Config            | YAML         | Hyperparameters, settings |
| Model Checkpoints | .pt / .zip   | Saved model weights       |
| Logs              | .log / .json | Training logs             |
| Notebooks         | .ipynb       | Kaggle training           |
| Documentation     | .md          | All docs                  |

---

## 🔧 Development Environment

### Required Installations

```
✅ Python 3.10.x
✅ OpenJDK 8
✅ Git
✅ Node.js (future dashboard)
✅ Docker (optional)
```

### Recommended IDE Setup (VS Code)

| Extension           | Purpose                 |
| ------------------- | ----------------------- |
| Python              | Python language support |
| Pylance             | Type checking           |
| GitLens             | Git integration         |
| YAML                | Config file support     |
| Markdown All in One | Documentation           |

---

## 🌐 External Services

| Service    | Purpose              | Required    |
| ---------- | -------------------- | ----------- |
| GitHub     | Code repository      | ✅ Yes      |
| Kaggle     | GPU training         | ✅ Yes      |
| PyPI       | Package installation | ✅ Yes      |
| Docker Hub | Container images     | ❌ Optional |

---

## 📎 Related Documents

- [guides/SETUP_GUIDE.md](guides/SETUP_GUIDE.md)
- [SYSTEM_BOUNDARIES.md](SYSTEM_BOUNDARIES.md)
