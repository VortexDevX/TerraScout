# 🏋️ Terra Scout Training

> Training scripts, configurations, and experiment management.

---

## 📁 Structure

```
training/
├── scripts/
│   ├── train.py           # Main training script
│   ├── evaluate.py        # Evaluation script
│   └── export_model.py    # Model export utilities
├── configs/
│   ├── training_config.yaml    # Training hyperparameters
│   └── hyperparameters.yaml    # Model hyperparameters
├── notebooks/
│   ├── train_kaggle.ipynb      # Kaggle training notebook
│   └── analysis.ipynb          # Results analysis
├── checkpoints/           # Saved model weights
├── logs/                  # Training logs (TensorBoard)
├── experiments/           # Experiment tracking
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🚀 Quick Start

### Local Training

```bash
# Activate environment
cd TerraScout
.\venv\Scripts\Activate.ps1

# Start training
python training/scripts/train.py

# With custom config
python training/scripts/train.py --config training/configs/training_config.yaml

# With overrides
python training/scripts/train.py --total-timesteps 500000 --learning-rate 0.0001
```

### Kaggle Training

1. Upload `training/notebooks/train_kaggle.ipynb` to Kaggle
2. Enable GPU accelerator
3. Run all cells
4. Download checkpoints when complete

---

## ⚙️ Configuration

### Training Config

```yaml
# training/configs/training_config.yaml

environment:
  name: "MineRLObtainDiamond-v0"
  max_episode_steps: 18000

algorithm:
  name: "PPO"
  learning_rate: 0.0003
  n_steps: 2048
  batch_size: 64

training:
  total_timesteps: 1000000
  eval_freq: 10000
  save_freq: 50000
```

### Key Parameters

| Parameter         | Description         | Recommended |
| ----------------- | ------------------- | ----------- |
| `total_timesteps` | Training duration   | 1M+         |
| `learning_rate`   | Update step size    | 3e-4        |
| `n_steps`         | Steps per update    | 2048        |
| `batch_size`      | Minibatch size      | 64          |
| `eval_freq`       | Evaluation interval | 10000       |

---

## 📊 Monitoring

### TensorBoard

```bash
# Start TensorBoard
tensorboard --logdir training/logs

# Open browser
# http://localhost:6006
```

### Key Metrics

| Metric           | Good Sign         | Bad Sign        |
| ---------------- | ----------------- | --------------- |
| `episode_reward` | Increasing        | Flat/Decreasing |
| `diamond_rate`   | Increasing        | Zero            |
| `policy_loss`    | Stable/Decreasing | Exploding       |
| `entropy`        | Gradual decrease  | Rapid collapse  |

---

## 💾 Checkpoints

### Automatic Saves

```
checkpoints/
├── model_50000_steps.zip
├── model_100000_steps.zip
├── model_best.zip          # Best eval reward
└── model_last.zip          # Most recent
```

### Loading Checkpoints

```python
from stable_baselines3 import PPO

# Load model
model = PPO.load("training/checkpoints/model_best.zip")

# Continue training
model.learn(total_timesteps=500000)
```

---

## 📈 Evaluation

```bash
# Evaluate trained model
python training/scripts/evaluate.py \
    --model training/checkpoints/model_best.zip \
    --episodes 100

# With video recording
python training/scripts/evaluate.py \
    --model training/checkpoints/model_best.zip \
    --episodes 10 \
    --record
```

---

## 📎 Related Documentation

- [Training Guide](../docs/guides/TRAINING_GUIDE.md)
- [RL Algorithms](../docs/research/RL_ALGORITHMS.md)
- [Reward Design](../docs/research/REWARD_DESIGN.md)
