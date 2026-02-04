# 🔄 Data Flow

> How data moves through the Terra Scout system.

---

## 📊 High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW OVERVIEW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐                                       ┌─────────────┐      │
│  │  Minecraft  │                                       │   Saved     │      │
│  │   Server    │                                       │   Model     │      │
│  └──────┬──────┘                                       └──────▲──────┘      │
│         │                                                     │             │
│         │ Game state via Minecraft protocol                   │ Weights     │
│         ▼                                                     │             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──┴──────────┐  │
│  │ Mineflayer  │───>│ Express.js  │───>│ Bridge      │───>│   PPO       │  │
│  │ Bot (Node)  │    │ HTTP API    │    │ Client (Py) │    │   Model     │  │
│  └──────┬──────┘    └─────────────┘    └─────────────┘    └──────┬──────┘  │
│         │                                                        │          │
│         │                                                        │ Action   │
│         │                                                        │ probs    │
│         │                                                        ▼          │
│         │           ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│         │           │   Reward    │<───│   Action    │<───│   Action    │  │
│         │<──────────│ Calculator  │    │   Mapper    │    │  Selector   │  │
│         │           └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                 │                                                 │
│         │                 ▼                                                 │
│         │           ┌─────────────┐                                        │
│         │           │  Rollout    │                                        │
│         │           │   Buffer    │                                        │
│         │           └──────┬──────┘                                        │
│         │                  │                                                │
│         │                  ▼                                                │
│         │           ┌─────────────┐    ┌─────────────┐                     │
│         │           │   Policy    │───>│  Metrics    │──> Logs/JSON        │
│         │           │   Update    │    │  Tracker    │                     │
│         │           └─────────────┘    └─────────────┘                     │
│         │                                                                   │
│         └───────────────────────────────────────────────────────────────>   │
│                                 (loop continues)                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📥 Input Data

### Raw Observation from Mineflayer Bot

```python
observation = {
    'position': {
        'x': float,              # World X coordinate
        'y': float,              # World Y coordinate (depth)
        'z': float,              # World Z coordinate
    },

    'health': float,             # 0.0 to 20.0
    'food': float,               # 0.0 to 20.0
    'yaw': float,                # Player rotation (radians)
    'pitch': float,              # Player look angle (radians)
    'onGround': bool,            # Is player on solid ground

    'inventory': {
        'diamond': int,
        'iron_ingot': int,
        'coal': int,
        'cobblestone': int,
        # ... other items
    },

    'nearbyBlocks': [
        {'name': str, 'position': {'x': int, 'y': int, 'z': int}},
        # ... up to ~300 blocks in 4-block radius
    ],

    'visibleOres': [
        {'name': str, 'position': {...}, 'distance': float, 'value': int},
        # ... exposed ore blocks sorted by value
    ],

    'inCave': bool,              # Detected large air pocket underground
    'atDiamondLevel': bool,      # Y between -64 and -50
    'dangerNearby': bool,        # Lava/fire within detection radius
    'diamondNearby': bool,       # Diamond ore visible
}
```

### Processed Observation (35 features)

```python
processed_observation = np.array([
    # Position (3)
    pos_x / 1000.0, pos_y / 320.0, pos_z / 1000.0,

    # Vitals (2)
    health / 20.0, food / 20.0,

    # Orientation (4)
    sin(yaw), cos(yaw), sin(pitch), cos(pitch),

    # Y-level info (5)
    y / 320.0, in_diamond_zone, below_sea_level, in_optimal_range, progress_into_zone,

    # Nearby blocks (10)
    ore_density, diamond_density, danger_density, stone_density, air_density,
    ore_proximity, diamond_proximity, diamond_visible, ore_visible, danger_nearby,

    # Inventory (8)
    diamonds, iron, coal, cobblestone, torches, has_diamond, has_pickaxe, total_items,

    # Exploration (3)
    visited_count, is_new_pos, depth_from_start,
], dtype=np.float32)  # Shape: (35,)
```

---

## 📤 Output Data

### Agent Action Output

```python
# Internal action representation
internal_action = {
    'move': int,        # 0=none, 1=forward, 2=back, 3=left, 4=right
    'camera': tuple,    # (pitch_delta, yaw_delta)
    'action': int       # 0=none, 1=attack, 2=jump, 3=sneak
}

# MineRL action format
minerl_action = {
    'forward': int,     # 0 or 1
    'back': int,        # 0 or 1
    'left': int,        # 0 or 1
    'right': int,       # 0 or 1
    'jump': int,        # 0 or 1
    'sneak': int,       # 0 or 1
    'sprint': int,      # 0 or 1
    'attack': int,      # 0 or 1
    'camera': tuple     # (pitch, yaw) in degrees
}
```

---

## 🔄 Training Data Flow

### Single Step

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          SINGLE STEP DATA FLOW                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TIME: t                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  State (s_t)                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────┐   │ │
│  │  │ pov: [64x64x3], inventory: {...}, health: 20.0              │   │ │
│  │  └─────────────────────────────────────────────────────────────┘   │ │
│  │         │                                                           │ │
│  │         ▼                                                           │ │
│  │  ┌─────────────┐         ┌─────────────┐                           │ │
│  │  │   Agent     │────────>│   Action    │                           │ │
│  │  │  .predict() │         │   a_t       │                           │ │
│  │  └─────────────┘         └──────┬──────┘                           │ │
│  │                                 │                                   │ │
│  │                                 ▼                                   │ │
│  │                          ┌─────────────┐                           │ │
│  │                          │ Environment │                           │ │
│  │                          │   .step()   │                           │ │
│  │                          └──────┬──────┘                           │ │
│  │                                 │                                   │ │
│  │                    ┌────────────┼────────────┐                     │ │
│  │                    ▼            ▼            ▼                     │ │
│  │              ┌──────────┐ ┌──────────┐ ┌──────────┐               │ │
│  │              │ State    │ │ Reward   │ │  Done    │               │ │
│  │              │ s_{t+1}  │ │ r_t      │ │  flag    │               │ │
│  │              └──────────┘ └──────────┘ └──────────┘               │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  TIME: t+1                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Experience Tuple: (s_t, a_t, r_t, s_{t+1}, done)                  │ │
│  │         │                                                           │ │
│  │         ▼                                                           │ │
│  │  ┌─────────────────┐                                               │ │
│  │  │ Experience      │                                               │ │
│  │  │ Buffer          │                                               │ │
│  │  │ [..., exp_t]    │                                               │ │
│  │  └─────────────────┘                                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Episode Data Structure

```python
episode_data = {
    'observations': List[dict],     # All observations
    'actions': List[dict],          # All actions taken
    'rewards': List[float],         # All rewards received
    'dones': List[bool],            # Termination flags
    'infos': List[dict],            # Additional info

    # Computed after episode
    'total_reward': float,
    'episode_length': int,
    'diamond_found': bool,
    'cause_of_death': Optional[str]
}
```

---

## 💾 Checkpoint Data

### Model Checkpoint Structure

```python
checkpoint = {
    'epoch': int,
    'global_step': int,

    'model_state_dict': {
        'feature_extractor': dict,
        'policy_net': dict,
        'value_net': dict
    },

    'optimizer_state_dict': dict,

    'config': dict,

    'metrics': {
        'best_reward': float,
        'best_diamond_rate': float,
        'training_time': float
    },

    'rng_states': {
        'python': ...,
        'numpy': ...,
        'torch': ...,
        'cuda': ...  # if applicable
    }
}
```

---

## 📊 Logging Data

### Training Metrics

```python
training_log = {
    'timestamp': str,
    'epoch': int,
    'episode': int,
    'step': int,

    # Per-episode metrics
    'episode_reward': float,
    'episode_length': int,
    'diamond_found': bool,

    # Aggregate metrics (per epoch)
    'mean_reward': float,
    'std_reward': float,
    'diamond_rate': float,
    'survival_rate': float,

    # Training metrics
    'policy_loss': float,
    'value_loss': float,
    'entropy': float,
    'learning_rate': float,

    # System metrics
    'fps': float,
    'memory_usage': float
}
```

### TensorBoard Data

```
logs/
└── experiment_name/
    └── events.out.tfevents.XXXXX
        ├── scalars/
        │   ├── reward/episode
        │   ├── reward/mean
        │   ├── loss/policy
        │   ├── loss/value
        │   ├── metrics/diamond_rate
        │   └── metrics/survival_rate
        └── histograms/
            ├── actions
            └── rewards
```

---

## 🔀 Data Transformation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DATA TRANSFORMATION PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RAW                 PROCESSED              TENSOR                BATCH     │
│  ───                 ─────────              ──────                ─────     │
│                                                                             │
│  pov                 normalized             torch.Tensor          stacked   │
│  (64,64,3)    ──>    (64,64,3)      ──>    (3,64,64)      ──>   (B,3,64,64)│
│  uint8 [0,255]       float [0,1]           float32               float32   │
│                                                                             │
│  inventory           selected items         torch.Tensor          stacked   │
│  {dict}       ──>    [diamond,iron,...]──> (N,)           ──>   (B,N)      │
│                      normalized                                             │
│                                                                             │
│  life_stats          normalized             torch.Tensor          stacked   │
│  {life,food,air}──>  [0,1] range    ──>    (3,)           ──>   (B,3)      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📎 Related Documents

- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
- [COMPONENT_DIAGRAM.md](COMPONENT_DIAGRAM.md)
- [../TECH_STACK.md](../TECH_STACK.md)
