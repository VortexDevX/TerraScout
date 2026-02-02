# 📦 Shared Module

> Shared constants, types, and utilities used across Terra Scout.

---

## 📁 Structure

```
shared/
├── __init__.py
├── README.md
├── constants/
│   ├── __init__.py
│   ├── minecraft.py    # Minecraft-specific constants
│   └── rewards.py      # Reward values
└── types/
    ├── __init__.py
    └── observations.py # Type definitions
```

---

## 🎮 Minecraft Constants

```python
from shared.constants.minecraft import (
    DIAMOND_Y_MIN,
    DIAMOND_Y_MAX,
    BLOCK_IDS,
    ACTION_KEYS
)

# Diamond spawns between Y=-64 and Y=16
print(f"Diamond range: {DIAMOND_Y_MIN} to {DIAMOND_Y_MAX}")
```

---

## 🎁 Reward Constants

```python
from shared.constants.rewards import (
    DIAMOND_FOUND_REWARD,
    DEATH_PENALTY,
    STEP_PENALTY
)

# Use in reward calculation
if found_diamond:
    reward = DIAMOND_FOUND_REWARD  # 1000.0
```

---

## 📝 Type Definitions

```python
from shared.types.observations import (
    Observation,
    ProcessedObservation,
    Action
)

# Type hints for better code
def process_obs(obs: Observation) -> ProcessedObservation:
    ...
```

---

## 🔧 Usage

Import in any module:

```python
# From agent
from shared.constants import minecraft, rewards

# Direct imports
from shared.constants.minecraft import DIAMOND_Y_MAX
from shared.constants.rewards import DIAMOND_FOUND_REWARD
```

---

## 📎 Related Documentation

- [Architecture Overview](../docs/architecture/SYSTEM_OVERVIEW.md)
- [Reward Design](../docs/research/REWARD_DESIGN.md)
