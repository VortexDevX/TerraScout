# 🛠️ Technology Stack

> Complete list of technologies, tools, and dependencies used in Terra Scout.

---

## 📊 Stack Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      TERRA SCOUT STACK                      │
├─────────────────────────────────────────────────────────────┤
│  TRAINING PLATFORM                                          │
│  └── Kaggle (GPU: T4/P100)                                  │
├─────────────────────────────────────────────────────────────┤
│  REINFORCEMENT LEARNING                                     │
│  ├── Stable-Baselines3 (RL algorithms)                      │
│  └── Gymnasium (Environment API)                            │
├─────────────────────────────────────────────────────────────┤
│  DEEP LEARNING                                              │
│  ├── PyTorch (Neural networks)                              │
│  └── TorchVision (Vision utilities)                         │
├─────────────────────────────────────────────────────────────┤
│  ENVIRONMENT                                                │
│  ├── MineRL (Minecraft RL environment)                      │
│  └── Minecraft Java Edition                                 │
├─────────────────────────────────────────────────────────────┤
│  LANGUAGE & RUNTIME                                         │
│  ├── Python 3.10                                            │
│  └── OpenJDK 8 (Java)                                       │
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
| `minerl`            | 1.0.x   | Minecraft RL environment |
| `gymnasium`         | 0.29.x  | Environment API standard |
| `stable-baselines3` | 2.x     | RL algorithms (PPO, DQN) |
| `torch`             | 2.x     | Neural network framework |
| `torchvision`       | 0.x     | Vision utilities         |
| `numpy`             | 1.24.x  | Numerical computing      |

### Utility Dependencies

| Package         | Version | Purpose                |
| --------------- | ------- | ---------------------- |
| `opencv-python` | 4.x     | Image processing       |
| `pillow`        | 10.x    | Image handling         |
| `pyyaml`        | 6.x     | Config file parsing    |
| `tqdm`          | 4.x     | Progress bars          |
| `tensorboard`   | 2.x     | Training visualization |
| `matplotlib`    | 3.x     | Plotting               |

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

## ☕ Java Requirements

| Component | Version   | Notes               |
| --------- | --------- | ------------------- |
| OpenJDK   | 8 (1.8.0) | Required by MineRL  |
| JAVA_HOME | Set       | Must point to JDK 8 |

---

## 🎮 MineRL Environment

### Supported Environments

| Environment              | Description                   | Use Case         |
| ------------------------ | ----------------------------- | ---------------- |
| `MineRLNavigateDense-v0` | Navigation with dense rewards | Initial testing  |
| `MineRLObtainDiamond-v0` | Full diamond obtaining task   | Main objective   |
| `MineRLTreechop-v0`      | Tree chopping task            | Simpler baseline |

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
