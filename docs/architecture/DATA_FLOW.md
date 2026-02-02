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
│  │    World    │                                       │   Model     │      │
│  └──────┬──────┘                                       └──────▲──────┘      │
│         │                                                     │             │
│         │ Raw pixels + game state                             │ Weights     │
│         ▼                                                     │             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──┴──────────┐  │
│  │   MineRL    │───>│ Observation │───>│   Feature   │───>│   Policy    │  │
│  │ Environment │    │  Wrapper    │    │  Extractor  │    │   Network   │  │
│  └──────┬──────┘    └─────────────┘    └─────────────┘    └──────┬──────┘  │
│         │                                                        │          │
│         │                                                        │ Action   │
│         │                                                        │ probs    │
│         │                                                        ▼          │
│         │           ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│         │           │   Reward    │<───│   Action    │<───│   Action    │  │
│         │<──────────│   Signal    │    │  Wrapper    │    │  Selector   │  │
│         │           └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                 │                                                 │
│         │                 │                                                 │
│         │                 ▼                                                 │
│         │           ┌─────────────┐                                        │
│         │           │  Experience │                                        │
│         │           │   Buffer    │                                        │
│         │           └──────┬──────┘                                        │
│         │                  │                                                │
│         │                  ▼                                                │
│         │           ┌─────────────┐    ┌─────────────┐                     │
│         │           │   Policy    │───>│   Logger    │──> Logs/Metrics    │
│         │           │   Update    │    └─────────────┘                     │
│         │           └─────────────┘                                        │
│         │                                                                   │
│         └───────────────────────────────────────────────────────────────>   │
│                                 (loop continues)                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📥 Input Data

### Raw Observation from MineRL

```python
observation = {
    'pov': np.ndarray,          # Shape: (64, 64, 3), dtype: uint8
                                 # First-person camera view

    'inventory': {
        'coal': int,
        'cobblestone': int,
        'diamond': int,
        'dirt': int,
        'iron_ore': int,
        # ... other items
    },

    'equipped_items': {
        'mainhand': {
            'damage': int,
            'maxDamage': int,
            'type': str
        }
    },

    'life_stats': {
        'life': float,          # 0.0 to 20.0
        'food': float,          # 0.0 to 20.0
        'air': float            # 0.0 to 300.0
    }
}
```

### Processed Observation

```python
processed_observation = {
    'visual': torch.Tensor,     # Shape: (3, 64, 64), normalized [0, 1]
    'inventory': torch.Tensor,  # Shape: (N,), relevant items only
    'health': torch.Tensor,     # Shape: (3,), [life, food, air] normalized
}
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
