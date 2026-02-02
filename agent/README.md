# 🤖 Terra Scout Agent

> Core agent module for autonomous Minecraft exploration.

---

## 📁 Structure

```
agent/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py           # Main agent class
│   │   ├── policy.py          # Policy implementation
│   │   └── trainer.py         # Training orchestration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── networks.py        # Neural network architectures
│   │   ├── feature_extractor.py  # CNN for observations
│   │   └── heads.py           # Policy and value heads
│   ├── environment/
│   │   ├── __init__.py
│   │   ├── wrappers.py        # Environment wrappers
│   │   ├── observation.py     # Observation processing
│   │   ├── action.py          # Action space handling
│   │   └── reward.py          # Custom reward functions
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Logging utilities
│       ├── config.py          # Configuration handling
│       ├── checkpoint.py      # Model saving/loading
│       └── metrics.py         # Metric calculations
├── configs/
│   └── default.yaml           # Default configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_agent.py
│   ├── test_models.py
│   └── test_environment.py
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
└── pyproject.toml
```

---

## 🚀 Quick Start

### Installation

```bash
# From agent directory
pip install -e .

# Or from root
pip install -e ./agent
```

### Basic Usage

```python
from agent.src.core import TerraScoutAgent
from agent.src.environment import create_environment

# Create environment
env = create_environment("MineRLObtainDiamond-v0")

# Create agent
agent = TerraScoutAgent(env, config_path="configs/default.yaml")

# Train
agent.train(total_timesteps=100000)

# Evaluate
results = agent.evaluate(n_episodes=10)
print(f"Diamond rate: {results['diamond_rate']:.2%}")
```

---

## 🧩 Components

### Core

| Component         | Description                                   |
| ----------------- | --------------------------------------------- |
| `TerraScoutAgent` | Main agent class orchestrating all components |
| `Policy`          | Action selection policy using neural networks |
| `Trainer`         | Training loop and optimization logic          |

### Models

| Component          | Description                                   |
| ------------------ | --------------------------------------------- |
| `FeatureExtractor` | CNN processing visual observations            |
| `PolicyNetwork`    | Actor network outputting action probabilities |
| `ValueNetwork`     | Critic network estimating state values        |

### Environment

| Component              | Description                           |
| ---------------------- | ------------------------------------- |
| `TerraScoutEnvWrapper` | Main environment wrapper              |
| `ObservationWrapper`   | Processes and normalizes observations |
| `ActionWrapper`        | Simplifies action space               |
| `RewardWrapper`        | Applies custom reward shaping         |

### Utils

| Component    | Description                         |
| ------------ | ----------------------------------- |
| `Logger`     | Structured logging with TensorBoard |
| `Config`     | YAML configuration management       |
| `Checkpoint` | Model serialization and loading     |
| `Metrics`    | Training and evaluation metrics     |

---

## ⚙️ Configuration

### Default Configuration

```yaml
# configs/default.yaml

agent:
  name: "TerraScout"
  version: "0.1.0"

model:
  feature_extractor:
    type: "CNN"
    channels: [32, 64, 64]
    kernel_sizes: [8, 4, 3]
    strides: [4, 2, 1]

  policy_net:
    hidden_sizes: [512, 256]
    activation: "relu"

  value_net:
    hidden_sizes: [512, 256]
    activation: "relu"

environment:
  name: "MineRLObtainDiamond-v0"
  frame_stack: 4
  frame_skip: 4
  grayscale: false
  resize: [64, 64]
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agent.py

# Run with verbose output
pytest -v
```

---

## 📊 Metrics

### Training Metrics

| Metric           | Description              |
| ---------------- | ------------------------ |
| `episode_reward` | Total reward per episode |
| `episode_length` | Steps per episode        |
| `policy_loss`    | Policy network loss      |
| `value_loss`     | Value network loss       |
| `entropy`        | Policy entropy           |

### Evaluation Metrics

| Metric                 | Description                   |
| ---------------------- | ----------------------------- |
| `diamond_rate`         | % episodes finding diamond    |
| `survival_rate`        | % episodes without death      |
| `avg_steps_to_diamond` | Average steps when successful |
| `mean_reward`          | Average episode reward        |

---

## 📎 Related Documentation

- [Training Guide](../docs/guides/TRAINING_GUIDE.md)
- [Architecture Overview](../docs/architecture/SYSTEM_OVERVIEW.md)
- [Reward Design](../docs/research/REWARD_DESIGN.md)
