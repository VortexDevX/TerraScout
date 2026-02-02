# 🎁 Reward Design

> Designing effective reward functions for Terra Scout.

---

## 📋 Overview

Reward design is critical for reinforcement learning success. A well-designed reward function guides the agent toward desired behavior while avoiding unintended shortcuts.

### The Challenge

```
┌─────────────────────────────────────────────────────────────┐
│                    THE SPARSE REWARD PROBLEM                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Finding diamonds in Minecraft:                             │
│                                                             │
│  ┌─────┐                                          ┌─────┐  │
│  │Start│ ──────────────────────────────────────── │💎   │  │
│  └─────┘     Thousands of steps, zero reward      └─────┘  │
│                                                             │
│  Problem: Agent receives no learning signal until the       │
│           very end. Random exploration is inefficient.      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Reward Components

### 1. Terminal Rewards

| Event           | Reward  | Rationale                    |
| --------------- | ------- | ---------------------------- |
| Diamond found   | +1000.0 | Primary objective            |
| Agent death     | -100.0  | Discourage reckless behavior |
| Episode timeout | -10.0   | Encourage efficiency         |

### 2. Progress Rewards (Shaping)

| Event                | Reward | Rationale                    |
| -------------------- | ------ | ---------------------------- |
| Y-level decrease     | +0.1   | Encourage going underground  |
| New area explored    | +0.05  | Encourage exploration        |
| Ore discovered (any) | +1.0   | Proxy for diamond-rich areas |
| Cave entrance found  | +0.5   | Encourage cave exploration   |

### 3. Penalty Signals

| Event             | Reward | Rationale                 |
| ----------------- | ------ | ------------------------- |
| Each step         | -0.001 | Encourage efficiency      |
| Repeated position | -0.1   | Discourage getting stuck  |
| Damage taken      | -1.0   | Encourage safety          |
| Invalid action    | -0.01  | Discourage wasted actions |

### 4. Auxiliary Rewards

| Event          | Reward | Rationale                 |
| -------------- | ------ | ------------------------- |
| Iron ore found | +2.0   | Often near diamonds       |
| Redstone found | +3.0   | Indicates correct Y-level |
| Lapis found    | +2.5   | Indicates correct Y-level |
| Gold ore found | +1.5   | Underground indicator     |

---

## 📊 Reward Function Design

### Version 1: Dense Rewards (Initial Training)

```python
def compute_reward_v1(obs, action, next_obs, info):
    """Dense reward for initial training."""
    reward = 0.0

    # Step penalty (encourage efficiency)
    reward -= 0.001

    # Diamond found (terminal)
    if info.get('diamond_found', False):
        return 1000.0

    # Death penalty (terminal)
    if info.get('agent_dead', False):
        return -100.0

    # Y-level progress
    current_y = next_obs.get('y_position', 64)
    if current_y < 16:  # Diamond level
        reward += 0.1 * (16 - current_y) / 80  # Normalized

    # Exploration bonus
    if info.get('new_block_visited', False):
        reward += 0.05

    # Ore discovery
    if info.get('ore_visible', False):
        reward += 0.5

    # Damage penalty
    health_delta = next_obs.get('health', 20) - obs.get('health', 20)
    if health_delta < 0:
        reward += health_delta * 0.5  # -0.5 per health point lost

    return reward
```

### Version 2: Shaped Rewards (Mid Training)

```python
def compute_reward_v2(obs, action, next_obs, info):
    """Shaped reward with reduced density."""
    reward = 0.0

    # Step penalty
    reward -= 0.001

    # Terminal rewards
    if info.get('diamond_found', False):
        return 1000.0
    if info.get('agent_dead', False):
        return -100.0

    # Y-level bonus (only at key thresholds)
    current_y = next_obs.get('y_position', 64)
    prev_y = obs.get('y_position', 64)

    if current_y <= 16 and prev_y > 16:
        reward += 5.0  # Entered diamond zone
    elif current_y <= 0 and prev_y > 0:
        reward += 10.0  # Deep diamond zone

    # Ore-based rewards
    ore_type = info.get('ore_in_view', None)
    ore_rewards = {
        'diamond_ore': 50.0,   # Seeing diamond (not mining)
        'redstone_ore': 3.0,
        'lapis_ore': 2.5,
        'iron_ore': 1.0,
        'gold_ore': 1.5
    }
    if ore_type in ore_rewards:
        reward += ore_rewards[ore_type]

    # Stuck penalty
    if info.get('position_unchanged', False):
        reward -= 0.1

    return reward
```

### Version 3: Sparse Rewards (Final Training)

```python
def compute_reward_v3(obs, action, next_obs, info):
    """Sparse reward for final training phase."""

    # Diamond found
    if info.get('diamond_found', False):
        return 1000.0

    # Death
    if info.get('agent_dead', False):
        return -100.0

    # Minimal step penalty
    return -0.0001
```

---

## 🔄 Reward Shaping Schedule

```
┌─────────────────────────────────────────────────────────────┐
│                  REWARD SHAPING SCHEDULE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Episodes:  0        50k      100k     150k     200k       │
│             │         │         │         │         │       │
│             ▼         ▼         ▼         ▼         ▼       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Dense    │ Dense   │ Shaped  │ Shaped  │ Sparse    │  │
│  │ v1       │ v1→v2   │ v2      │ v2→v3   │ v3        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Shaping     100%      75%       50%       25%       0%    │
│  Intensity                                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Implementation

```python
def get_reward_function(episode_num, total_episodes=200000):
    """Get appropriate reward function based on training progress."""
    progress = episode_num / total_episodes

    if progress < 0.25:
        return compute_reward_v1  # Dense
    elif progress < 0.5:
        # Blend v1 and v2
        return lambda *args: (
            0.5 * compute_reward_v1(*args) +
            0.5 * compute_reward_v2(*args)
        )
    elif progress < 0.75:
        return compute_reward_v2  # Shaped
    else:
        # Blend v2 and v3
        blend = (progress - 0.75) / 0.25
        return lambda *args: (
            (1 - blend) * compute_reward_v2(*args) +
            blend * compute_reward_v3(*args)
        )
```

---

## ⚠️ Reward Hacking Prevention

### Common Exploits

| Exploit             | Description                             | Prevention                      |
| ------------------- | --------------------------------------- | ------------------------------- |
| Suicide for reset   | Agent dies to reset if stuck            | Death penalty > potential gain  |
| Y-level oscillation | Move up/down repeatedly                 | Only reward net Y decrease      |
| Stuck in corner     | Get exploration bonus by looking around | Require actual position change  |
| Ore camping         | Stay near ore without mining            | Diminishing returns on same ore |

### Prevention Strategies

```python
class RewardTracker:
    """Track state to prevent reward hacking."""

    def __init__(self):
        self.visited_positions = set()
        self.ore_discoveries = {}
        self.lowest_y = 64
        self.steps_at_position = 0
        self.last_position = None

    def compute_safe_reward(self, obs, action, next_obs, info):
        reward = 0.0
        current_pos = self._get_position(next_obs)

        # Position change check
        if current_pos == self.last_position:
            self.steps_at_position += 1
            if self.steps_at_position > 50:
                reward -= 0.5  # Stuck penalty
        else:
            self.steps_at_position = 0

        # Y-level: only reward new lows
        current_y = next_obs.get('y_position', 64)
        if current_y < self.lowest_y:
            reward += 0.1 * (self.lowest_y - current_y)
            self.lowest_y = current_y

        # Exploration: only reward truly new positions
        if current_pos not in self.visited_positions:
            reward += 0.05
            self.visited_positions.add(current_pos)

        # Ore: diminishing returns
        ore_type = info.get('ore_in_view', None)
        if ore_type:
            times_seen = self.ore_discoveries.get(ore_type, 0)
            ore_reward = 1.0 / (1 + times_seen)  # Diminishes
            reward += ore_reward
            self.ore_discoveries[ore_type] = times_seen + 1

        self.last_position = current_pos
        return reward
```

---

## 📈 Reward Normalization

### Why Normalize?

- Prevents gradient explosion
- Stabilizes training
- Makes hyperparameters transferable

### Normalization Methods

```python
class RewardNormalizer:
    """Running normalization of rewards."""

    def __init__(self, clip=10.0):
        self.mean = 0.0
        self.var = 1.0
        self.count = 0
        self.clip = clip

    def normalize(self, reward):
        self.count += 1
        delta = reward - self.mean
        self.mean += delta / self.count
        self.var += delta * (reward - self.mean)

        std = max(np.sqrt(self.var / self.count), 1e-8)
        normalized = (reward - self.mean) / std
        return np.clip(normalized, -self.clip, self.clip)
```

---

## 📊 Reward Configuration

### YAML Configuration

```yaml
# training/configs/reward_config.yaml

reward:
  version: "v2" # v1, v2, or v3

  terminal:
    diamond_found: 1000.0
    agent_death: -100.0
    timeout: -10.0

  progress:
    y_level_decrease: 0.1
    new_area_explored: 0.05
    ore_discovered: 1.0
    cave_found: 0.5

  penalties:
    step: -0.001
    repeated_position: -0.1
    damage_taken: -1.0
    invalid_action: -0.01

  ore_values:
    diamond_ore: 50.0
    redstone_ore: 3.0
    lapis_ore: 2.5
    iron_ore: 1.0
    gold_ore: 1.5

  normalization:
    enabled: true
    clip: 10.0

  shaping:
    schedule: "linear_decay"
    start_episode: 0
    end_episode: 150000
```

---

## 📎 Related Documents

- [RL_ALGORITHMS.md](RL_ALGORITHMS.md)
- [REFERENCES.md](REFERENCES.md)
- [../architecture/DATA_FLOW.md](../architecture/DATA_FLOW.md)
