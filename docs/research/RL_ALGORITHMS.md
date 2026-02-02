# 🧠 Reinforcement Learning Algorithms

> Analysis of RL algorithms for Terra Scout.

---

## 📋 Overview

This document analyzes reinforcement learning algorithms suitable for the Terra Scout diamond-finding task.

### Task Characteristics

| Characteristic    | Value                          | Implication                     |
| ----------------- | ------------------------------ | ------------------------------- |
| Observation Space | High-dimensional (images)      | Need function approximation     |
| Action Space      | Discrete + Continuous (camera) | Hybrid action handling          |
| Reward Density    | Sparse (diamond rare)          | Need exploration strategies     |
| Episode Length    | Long (thousands of steps)      | Need temporal credit assignment |
| Environment       | Stochastic, complex            | Need robust learning            |

---

## 🏆 Algorithm Comparison

### Quick Comparison

| Algorithm  | Type            | Sample Efficiency | Stability | Complexity | Recommendation |
| ---------- | --------------- | ----------------- | --------- | ---------- | -------------- |
| **PPO**    | Policy Gradient | Medium            | High      | Low        | ⭐ Primary     |
| **DQN**    | Value-Based     | Medium            | Medium    | Medium     | ⭐ Alternative |
| **A2C**    | Actor-Critic    | Low               | Medium    | Low        | Baseline       |
| **SAC**    | Actor-Critic    | High              | High      | High       | Future         |
| **IMPALA** | Distributed     | Very High         | High      | Very High  | Not for MVP    |

---

## 1️⃣ PPO (Proximal Policy Optimization)

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         PPO                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Actor     │    │   Critic    │    │   Clip      │     │
│  │  (Policy)   │    │  (Value)    │    │  Objective  │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                            ▼                                │
│                   Stable Policy Updates                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### How It Works

1. Collect trajectories using current policy
2. Compute advantages (how much better/worse than expected)
3. Update policy with clipped objective (prevents large updates)
4. Update value function
5. Repeat

### Key Equations

```
Policy Objective:
L^CLIP(θ) = E[min(r_t(θ) * A_t, clip(r_t(θ), 1-ε, 1+ε) * A_t)]

Where:
- r_t(θ) = π_θ(a|s) / π_θ_old(a|s)  (probability ratio)
- A_t = advantage estimate
- ε = clip parameter (typically 0.2)
```

### Hyperparameters

| Parameter       | Typical Value | Description                |
| --------------- | ------------- | -------------------------- |
| `learning_rate` | 3e-4          | Step size for updates      |
| `n_steps`       | 2048          | Steps before update        |
| `batch_size`    | 64            | Minibatch size             |
| `n_epochs`      | 10            | Epochs per update          |
| `gamma`         | 0.99          | Discount factor            |
| `gae_lambda`    | 0.95          | GAE parameter              |
| `clip_range`    | 0.2           | Clipping parameter         |
| `ent_coef`      | 0.01          | Entropy bonus              |
| `vf_coef`       | 0.5           | Value function coefficient |

### Pros & Cons

| Pros                            | Cons                                 |
| ------------------------------- | ------------------------------------ |
| ✅ Stable training              | ⚠️ On-policy (less sample efficient) |
| ✅ Simple to implement          | ⚠️ Sensitive to hyperparameters      |
| ✅ Works well with images       | ⚠️ Can plateau early                 |
| ✅ Good default choice          |                                      |
| ✅ SB3 implementation available |                                      |

### Suitability for Terra Scout

```
Overall Suitability: ⭐⭐⭐⭐⭐ (5/5)

✅ Handles image observations well
✅ Stable with sparse rewards
✅ Works with hybrid action spaces
✅ Well-tested in MineRL competitions
✅ Good SB3 implementation
```

---

## 2️⃣ DQN (Deep Q-Network)

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         DQN                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Q-Net     │    │   Target    │    │   Replay    │     │
│  │  (Online)   │    │   Q-Net     │    │   Buffer    │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                            ▼                                │
│                    Q-Value Learning                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### How It Works

1. Store experiences in replay buffer
2. Sample random batch from buffer
3. Compute target Q-values using target network
4. Update online network to minimize TD error
5. Periodically update target network
6. Select actions using ε-greedy

### Key Equations

```
Q-Learning Update:
Q(s, a) ← Q(s, a) + α * [r + γ * max_a' Q(s', a') - Q(s, a)]

Loss Function:
L(θ) = E[(r + γ * max_a' Q_target(s', a') - Q(s, a; θ))^2]
```

### Hyperparameters

| Parameter       | Typical Value | Description                  |
| --------------- | ------------- | ---------------------------- |
| `learning_rate` | 1e-4          | Step size for updates        |
| `buffer_size`   | 1000000       | Replay buffer size           |
| `batch_size`    | 32            | Minibatch size               |
| `gamma`         | 0.99          | Discount factor              |
| `epsilon_start` | 1.0           | Initial exploration          |
| `epsilon_end`   | 0.05          | Final exploration            |
| `epsilon_decay` | 0.995         | Decay rate                   |
| `target_update` | 10000         | Steps between target updates |

### Pros & Cons

| Pros                                | Cons                               |
| ----------------------------------- | ---------------------------------- |
| ✅ Sample efficient (replay buffer) | ❌ Discrete actions only           |
| ✅ Off-policy learning              | ⚠️ Overestimation bias             |
| ✅ Stable with target network       | ⚠️ Struggles with high-dim actions |
| ✅ Well understood                  | ⚠️ Needs action discretization     |

### Suitability for Terra Scout

```
Overall Suitability: ⭐⭐⭐ (3/5)

✅ Good sample efficiency
✅ Well-understood algorithm
⚠️ Requires discretizing camera actions
⚠️ May struggle with complex action space
❌ Not ideal for continuous actions
```

---

## 3️⃣ A2C (Advantage Actor-Critic)

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         A2C                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐              ┌─────────────┐              │
│  │   Actor     │              │   Critic    │              │
│  │  (Policy)   │◄────────────►│  (Value)    │              │
│  └──────┬──────┘   Advantage  └──────┬──────┘              │
│         │                            │                      │
│         └────────────────────────────┘                      │
│                       │                                     │
│                       ▼                                     │
│              Synchronized Updates                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### How It Works

1. Run policy for n steps
2. Compute returns and advantages
3. Update actor using policy gradient with advantage
4. Update critic using value loss
5. Repeat synchronously

### Key Equations

```
Policy Gradient:
∇_θ J(θ) = E[∇_θ log π_θ(a|s) * A(s, a)]

Advantage:
A(s, a) = Q(s, a) - V(s) ≈ r + γV(s') - V(s)
```

### Suitability for Terra Scout

```
Overall Suitability: ⭐⭐⭐ (3/5)

✅ Simpler than PPO
✅ Lower variance than REINFORCE
⚠️ Less stable than PPO
⚠️ Lower sample efficiency
```

---

## 4️⃣ SAC (Soft Actor-Critic)

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         SAC                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │   Actor     │   │  Critic 1   │   │  Critic 2   │       │
│  │ (Stochastic)│   │  (Q-value)  │   │  (Q-value)  │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
│         │                  │                 │              │
│         └──────────────────┴─────────────────┘              │
│                            │                                │
│                            ▼                                │
│              Entropy-Regularized Learning                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Suitability for Terra Scout

```
Overall Suitability: ⭐⭐⭐⭐ (4/5) - Future consideration

✅ Very sample efficient
✅ Automatic entropy tuning
✅ Great for continuous actions
⚠️ More complex implementation
⚠️ May be overkill for MVP
```

---

## 🎯 Recommendation for Terra Scout

### Primary Choice: PPO

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOMMENDED: PPO                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Reasons:                                                   │
│  ├── Proven in MineRL competitions                         │
│  ├── Stable training with sparse rewards                   │
│  ├── Handles image + discrete/continuous actions           │
│  ├── Excellent SB3 implementation                          │
│  ├── Good documentation and community support              │
│  └── Reasonable sample efficiency                          │
│                                                             │
│  Configuration:                                             │
│  ├── Policy: CnnPolicy (for image observations)            │
│  ├── n_steps: 2048                                         │
│  ├── batch_size: 64                                        │
│  ├── learning_rate: 3e-4                                   │
│  └── clip_range: 0.2                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Fallback: DQN with Discretized Actions

If PPO struggles, consider DQN with:

- Discretized camera movements
- Simplified action space
- Larger replay buffer

### Future Exploration: SAC

After MVP, consider SAC for:

- Better sample efficiency
- More exploration via entropy
- Continuous camera control

---

## 📊 Training Strategy

### Curriculum Learning

```
Stage 1: Simple Navigation
├── Flat terrain
├── Visible target
└── Dense rewards

Stage 2: Underground Navigation
├── Cave systems
├── Hidden targets
└── Shaped rewards

Stage 3: Diamond Finding
├── Full environment
├── Sparse rewards
└── Full complexity
```

### Reward Shaping Schedule

```
Early Training:
├── Heavy shaping (guide exploration)
└── Frequent rewards

Mid Training:
├── Reduce shaping
└── Transition to sparse

Late Training:
├── Minimal shaping
└── Pure task reward
```

---

## 📎 Related Documents

- [REWARD_DESIGN.md](REWARD_DESIGN.md)
- [REFERENCES.md](REFERENCES.md)
- [../architecture/SYSTEM_OVERVIEW.md](../architecture/SYSTEM_OVERVIEW.md)
