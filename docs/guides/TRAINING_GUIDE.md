# 🏋️ Training Guide

> How to train the Terra Scout agent.

---

## 📋 Overview

This guide covers:

1. Local training (development/testing)
2. Kaggle training (full training with GPU)
3. Monitoring and evaluation
4. Checkpointing and resuming

---

## 🖥️ Local Training

### When to Use Local Training

- Quick experiments
- Debugging
- Testing code changes
- Short training runs (<1 hour)

### Basic Training Command

```powershell
cd TerraScout
.\venv\Scripts\Activate.ps1

python training/scripts/train.py
```

### Training with Custom Config

```powershell
python training/scripts/train.py --config training/configs/training_config.yaml
```

### Training with Overrides

```powershell
python training/scripts/train.py \
    --total-timesteps 100000 \
    --learning-rate 0.0003 \
    --n-steps 2048
```

---

## 🌐 Kaggle Training

### Why Kaggle?

| Feature      | Local (RTX 2050) | Kaggle (T4/P100) |
| ------------ | ---------------- | ---------------- |
| VRAM         | 4 GB             | 16 GB            |
| Session Time | Unlimited        | 12 hours         |
| Cost         | Electricity      | Free             |
| Best For     | Development      | Full training    |

### Step 1: Prepare Kaggle Notebook

Create `training/notebooks/train_kaggle.ipynb`:

```python
# Cell 1: Setup
!pip install minerl stable-baselines3[extra] gymnasium

# Cell 2: Clone repo
!git clone https://github.com/VortexDevX/TerraScout.git
%cd TerraScout

# Cell 3: Verify GPU
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Cell 4: Training (see full notebook in repo)
```

### Step 2: Upload to Kaggle

1. Go to https://kaggle.com/code
2. Create new notebook
3. Copy cells from `train_kaggle.ipynb`
4. Enable GPU: Settings → Accelerator → GPU T4 x2

### Step 3: Run Training

- Click "Run All"
- Monitor progress in output
- Training auto-saves checkpoints

### Step 4: Download Results

```python
# In Kaggle notebook, last cell:
from kaggle.api.kaggle_api_extended import KaggleApi

# Checkpoints are saved to /kaggle/working/checkpoints/
# Download via Kaggle UI or API
```

---

## ⚙️ Training Configuration

### Configuration File Structure

```yaml
# training/configs/training_config.yaml

# Environment settings
environment:
  name: "MineRLObtainDiamond-v0"
  max_episode_steps: 18000 # 15 minutes at 20 TPS

# Algorithm settings
algorithm:
  name: "PPO"
  policy: "CnnPolicy"

# Hyperparameters
hyperparameters:
  learning_rate: 0.0003
  n_steps: 2048
  batch_size: 64
  n_epochs: 10
  gamma: 0.99
  gae_lambda: 0.95
  clip_range: 0.2
  ent_coef: 0.01
  vf_coef: 0.5
  max_grad_norm: 0.5

# Training settings
training:
  total_timesteps: 1000000
  eval_freq: 10000
  n_eval_episodes: 5
  save_freq: 50000

# Logging
logging:
  log_dir: "training/logs"
  tensorboard: true
  verbose: 1

# Checkpointing
checkpoint:
  save_dir: "training/checkpoints"
  save_best: true
  save_last: true
```

### Hyperparameter Recommendations

| Parameter       | Conservative | Balanced | Aggressive |
| --------------- | ------------ | -------- | ---------- |
| `learning_rate` | 1e-4         | 3e-4     | 1e-3       |
| `n_steps`       | 4096         | 2048     | 1024       |
| `batch_size`    | 32           | 64       | 128        |
| `n_epochs`      | 5            | 10       | 20         |
| `clip_range`    | 0.1          | 0.2      | 0.3        |
| `ent_coef`      | 0.001        | 0.01     | 0.05       |

---

## 📊 Monitoring Training

### TensorBoard

Start TensorBoard:

```powershell
tensorboard --logdir training/logs
```

Open http://localhost:6006 in browser.

### Key Metrics to Watch

| Metric               | Good Sign            | Bad Sign             |
| -------------------- | -------------------- | -------------------- |
| `episode_reward`     | Increasing trend     | Flat or decreasing   |
| `episode_length`     | Stable or increasing | Very short (dying)   |
| `policy_loss`        | Decreasing, stable   | Exploding, NaN       |
| `value_loss`         | Decreasing           | Exploding            |
| `entropy`            | Gradual decrease     | Too fast decrease    |
| `explained_variance` | Approaching 1.0      | Negative or very low |

### Training Progress Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING PROGRESS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Episode Reward                                             │
│  ▲                                                          │
│  │                                        ╭────────         │
│  │                              ╭─────────╯                 │
│  │                    ╭─────────╯                           │
│  │          ╭─────────╯                                     │
│  │ ─────────╯                                               │
│  └──────────────────────────────────────────────────▶       │
│    0        250k      500k      750k      1M     Steps      │
│                                                             │
│  Diamond Rate                                               │
│  ▲                                                          │
│  │                                             ╭──── 60%    │
│  │                                    ╭────────╯            │
│  │                          ╭─────────╯                     │
│  │              ╭───────────╯                               │
│  │ ─────────────╯                                    0%     │
│  └──────────────────────────────────────────────────▶       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 Checkpointing

### Automatic Checkpointing

Checkpoints are saved automatically based on config:

```
training/checkpoints/
├── model_50000_steps.zip
├── model_100000_steps.zip
├── model_150000_steps.zip
├── model_best.zip          # Best evaluation reward
└── model_last.zip          # Most recent
```

### Manual Checkpointing

```python
# During training
model.save("training/checkpoints/manual_checkpoint")

# Load checkpoint
from stable_baselines3 import PPO
model = PPO.load("training/checkpoints/manual_checkpoint")
```

### Resuming Training

```powershell
python training/scripts/train.py \
    --resume training/checkpoints/model_last.zip \
    --total-timesteps 2000000
```

---

## 📈 Evaluation

### Running Evaluation

```powershell
python training/scripts/evaluate.py \
    --model training/checkpoints/model_best.zip \
    --episodes 100
```

### Evaluation Metrics

| Metric               | Description                | Target     |
| -------------------- | -------------------------- | ---------- |
| Diamond Rate         | % episodes finding diamond | >60%       |
| Avg Steps to Diamond | Steps when successful      | <10000     |
| Survival Rate        | % episodes not dying       | >70%       |
| Avg Episode Reward   | Mean reward per episode    | Increasing |

### Evaluation Output

```
========================================
Evaluation Results (100 episodes)
========================================

Diamond Discovery:
  - Found: 67/100 (67.0%)
  - Avg steps to diamond: 8432

Survival:
  - Survived: 78/100 (78.0%)
  - Avg lifespan: 12043 steps

Rewards:
  - Mean: 245.7
  - Std: 89.3
  - Min: -45.2
  - Max: 1023.5

========================================
```

---

## 🎓 Training Curriculum

### Stage 1: Basic Navigation (Optional)

```yaml
# Use simpler environment first
environment:
  name: "MineRLNavigateDense-v0"
training:
  total_timesteps: 100000
```

### Stage 2: Tree Chopping (Optional)

```yaml
environment:
  name: "MineRLTreechop-v0"
training:
  total_timesteps: 200000
```

### Stage 3: Diamond Finding (Main)

```yaml
environment:
  name: "MineRLObtainDiamond-v0"
training:
  total_timesteps: 1000000
```

---

## ⚠️ Common Training Issues

| Issue                   | Symptom               | Solution                                    |
| ----------------------- | --------------------- | ------------------------------------------- |
| No learning             | Flat reward curve     | Check reward function, increase exploration |
| Catastrophic forgetting | Reward drops suddenly | Reduce learning rate, smaller updates       |
| Dying too often         | Short episodes        | Increase death penalty, add safety rewards  |
| Stuck behavior          | Repeated actions      | Add stuck penalty, curiosity bonus          |
| OOM error               | CUDA out of memory    | Reduce batch size, n_steps                  |

---

## 📎 Related Documents

- [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [../research/RL_ALGORITHMS.md](../research/RL_ALGORITHMS.md)
- [../research/REWARD_DESIGN.md](../research/REWARD_DESIGN.md)
