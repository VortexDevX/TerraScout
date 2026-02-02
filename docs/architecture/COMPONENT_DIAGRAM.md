# 🧩 Component Diagram

> Detailed breakdown of Terra Scout components and their relationships.

---

## 📦 Agent Module Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              agent/                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  src/                                                                       │
│  ├── __init__.py                                                            │
│  │                                                                          │
│  ├── core/                                                                  │
│  │   ├── __init__.py                                                        │
│  │   ├── agent.py              # Main agent class                           │
│  │   ├── policy.py             # Policy implementation                      │
│  │   └── trainer.py            # Training logic                             │
│  │                                                                          │
│  ├── models/                                                                │
│  │   ├── __init__.py                                                        │
│  │   ├── networks.py           # Neural network architectures               │
│  │   ├── feature_extractor.py  # CNN for observations                       │
│  │   └── heads.py              # Policy and value heads                     │
│  │                                                                          │
│  ├── environment/                                                           │
│  │   ├── __init__.py                                                        │
│  │   ├── wrappers.py           # Environment wrappers                       │
│  │   ├── observation.py        # Observation processing                     │
│  │   ├── action.py             # Action space handling                      │
│  │   └── reward.py             # Custom reward functions                    │
│  │                                                                          │
│  └── utils/                                                                 │
│      ├── __init__.py                                                        │
│      ├── logger.py             # Logging utilities                          │
│      ├── config.py             # Configuration handling                     │
│      ├── checkpoint.py         # Model saving/loading                       │
│      └── metrics.py            # Metric calculations                        │
│                                                                             │
│  configs/                                                                   │
│  └── default.yaml              # Default configuration                      │
│                                                                             │
│  tests/                                                                     │
│  ├── __init__.py                                                            │
│  ├── conftest.py               # Test fixtures                              │
│  ├── test_agent.py                                                          │
│  ├── test_models.py                                                         │
│  └── test_environment.py                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Training Module Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              training/                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  scripts/                                                                   │
│  ├── train.py                  # Main training entry point                  │
│  ├── evaluate.py               # Evaluation script                          │
│  └── export_model.py           # Model export utilities                     │
│                                                                             │
│  configs/                                                                   │
│  ├── training_config.yaml      # Training hyperparameters                   │
│  └── hyperparameters.yaml      # Model hyperparameters                      │
│                                                                             │
│  notebooks/                                                                 │
│  ├── train_kaggle.ipynb        # Kaggle training notebook                   │
│  └── analysis.ipynb            # Results analysis                           │
│                                                                             │
│  checkpoints/                  # Saved model weights                        │
│  ├── .gitkeep                                                               │
│  └── [model_epoch_X.pt]                                                     │
│                                                                             │
│  logs/                         # Training logs                              │
│  ├── .gitkeep                                                               │
│  └── [tensorboard_logs/]                                                    │
│                                                                             │
│  experiments/                  # Experiment tracking                        │
│  ├── .gitkeep                                                               │
│  └── [experiment_YYYYMMDD/]                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Shared Module Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              shared/                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  __init__.py                                                                │
│                                                                             │
│  constants/                                                                 │
│  ├── __init__.py                                                            │
│  ├── minecraft.py              # Minecraft-specific constants               │
│  │   ├── DIAMOND_Y_MIN         # Minimum Y for diamonds (-64)               │
│  │   ├── DIAMOND_Y_MAX         # Maximum Y for diamonds (16)                │
│  │   ├── BLOCK_IDS             # Block type identifiers                     │
│  │   └── ACTION_MAPPINGS       # Action name to ID mappings                 │
│  │                                                                          │
│  └── rewards.py                # Reward constants                           │
│      ├── DIAMOND_FOUND         # Reward for finding diamond                 │
│      ├── DEATH_PENALTY         # Penalty for dying                          │
│      ├── STEP_PENALTY          # Small penalty per step                     │
│      └── EXPLORE_BONUS         # Bonus for new areas                        │
│                                                                             │
│  types/                                                                     │
│  ├── __init__.py                                                            │
│  └── observations.py           # Type definitions for observations          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Component Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPONENT RELATIONSHIPS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                           ┌─────────────────┐                               │
│                           │   train.py      │                               │
│                           └────────┬────────┘                               │
│                                    │                                        │
│                    ┌───────────────┼───────────────┐                        │
│                    │               │               │                        │
│                    ▼               ▼               ▼                        │
│           ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│           │   config    │  │    agent    │  │  wrappers   │                │
│           │   loader    │  │    core     │  │             │                │
│           └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│                  │                │                │                        │
│                  │                ▼                │                        │
│                  │       ┌─────────────┐           │                        │
│                  │       │   models/   │           │                        │
│                  │       │  networks   │           │                        │
│                  │       └──────┬──────┘           │                        │
│                  │              │                  │                        │
│                  └──────────────┼──────────────────┘                        │
│                                 │                                           │
│                                 ▼                                           │
│                        ┌─────────────────┐                                  │
│                        │     shared/     │                                  │
│                        │   constants     │                                  │
│                        └────────┬────────┘                                  │
│                                 │                                           │
│                                 ▼                                           │
│                        ┌─────────────────┐                                  │
│                        │     MineRL      │                                  │
│                        │   Environment   │                                  │
│                        └─────────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Component Responsibility Matrix

| Component       | Creates         | Uses                    | Used By               |
| --------------- | --------------- | ----------------------- | --------------------- |
| `train.py`      | Training loop   | Agent, Config, Wrappers | Developer             |
| `agent.py`      | Agent instance  | Policy, Models          | train.py, evaluate.py |
| `policy.py`     | Policy logic    | Networks                | Agent                 |
| `networks.py`   | Neural nets     | PyTorch                 | Policy                |
| `wrappers.py`   | Env wrappers    | MineRL, Constants       | train.py              |
| `config.py`     | Config objects  | YAML files              | All modules           |
| `checkpoint.py` | Save/Load logic | PyTorch                 | Agent, train.py       |
| `constants/`    | Constants       | -                       | All modules           |

---

## 🔌 Interface Definitions

### Agent Interface

```python
class Agent:
    def __init__(self, config: Config) -> None: ...
    def select_action(self, observation: dict) -> dict: ...
    def update(self, experiences: List[Experience]) -> dict: ...
    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...
```

### Environment Wrapper Interface

```python
class TerraScoutEnvWrapper(gymnasium.Wrapper):
    def __init__(self, env: gymnasium.Env) -> None: ...
    def reset(self) -> Tuple[dict, dict]: ...
    def step(self, action: dict) -> Tuple[dict, float, bool, bool, dict]: ...
    def compute_reward(self, obs: dict, action: dict, next_obs: dict) -> float: ...
```

### Config Interface

```python
class Config:
    def __init__(self, path: str) -> None: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def to_dict(self) -> dict: ...
```

---

## 📎 Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
- [DATA_FLOW.md](DATA_FLOW.md)
