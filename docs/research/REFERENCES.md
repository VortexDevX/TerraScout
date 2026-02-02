# 📚 References

> Papers, resources, and references for Terra Scout development.

---

## 📄 Academic Papers

### Reinforcement Learning Foundations

| Paper                                                                                                  | Authors         | Year | Relevance        |
| ------------------------------------------------------------------------------------------------------ | --------------- | ---- | ---------------- |
| [Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602)                      | Mnih et al.     | 2013 | DQN foundations  |
| [Human-level control through deep reinforcement learning](https://www.nature.com/articles/nature14236) | Mnih et al.     | 2015 | DQN Nature paper |
| [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)                            | Schulman et al. | 2017 | PPO algorithm    |
| [Soft Actor-Critic](https://arxiv.org/abs/1801.01290)                                                  | Haarnoja et al. | 2018 | SAC algorithm    |
| [Asynchronous Methods for Deep RL](https://arxiv.org/abs/1602.01783)                                   | Mnih et al.     | 2016 | A3C algorithm    |

### MineRL & Minecraft RL

| Paper                                                                                         | Authors           | Year | Relevance               |
| --------------------------------------------------------------------------------------------- | ----------------- | ---- | ----------------------- |
| [MineRL: A Large-Scale Dataset of Minecraft Demonstrations](https://arxiv.org/abs/1907.13440) | Guss et al.       | 2019 | MineRL dataset          |
| [MineRL Diamond Challenge](https://arxiv.org/abs/2106.03748)                                  | Kanervisto et al. | 2021 | Competition overview    |
| [Hierarchical RL for Minecraft](https://arxiv.org/abs/2003.06066)                             | Various           | 2020 | Hierarchical approaches |
| [Video PreTraining (VPT)](https://arxiv.org/abs/2206.11795)                                   | Baker et al.      | 2022 | Pretraining on videos   |

### Exploration & Reward Shaping

| Paper                                                                                                                                                | Authors       | Year | Relevance             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ---- | --------------------- |
| [Curiosity-driven Exploration](https://arxiv.org/abs/1705.05363)                                                                                     | Pathak et al. | 2017 | Intrinsic motivation  |
| [Random Network Distillation](https://arxiv.org/abs/1810.12894)                                                                                      | Burda et al.  | 2018 | Exploration bonus     |
| [Policy Invariance Under Reward Transformations](https://people.eecs.berkeley.edu/~pabbeel/cs287-fa09/readings/NgHaradaRussell-shaping-ICML1999.pdf) | Ng et al.     | 1999 | Reward shaping theory |
| [Reward is enough](https://www.sciencedirect.com/science/article/pii/S0004370221000862)                                                              | Silver et al. | 2021 | Reward hypothesis     |

### Visual RL

| Paper                                                                                      | Authors          | Year | Relevance             |
| ------------------------------------------------------------------------------------------ | ---------------- | ---- | --------------------- |
| [CURL: Contrastive Unsupervised RL](https://arxiv.org/abs/2004.04136)                      | Srinivas et al.  | 2020 | Visual representation |
| [Data-Efficient RL with Self-Predictive Representations](https://arxiv.org/abs/2007.05929) | Schwarzer et al. | 2020 | SPR for visual RL     |
| [Image Augmentation Is All You Need](https://arxiv.org/abs/2004.13649)                     | Kostrikov et al. | 2020 | DrQ augmentation      |

---

## 🌐 Online Resources

### MineRL Resources

| Resource             | URL                                  | Description       |
| -------------------- | ------------------------------------ | ----------------- |
| MineRL Documentation | https://minerl.io/docs/              | Official docs     |
| MineRL GitHub        | https://github.com/minerllabs/minerl | Source code       |
| MineRL Discord       | https://discord.gg/minerl            | Community         |
| MineRL Competition   | https://minerl.io/competition/       | Past competitions |

### RL Libraries

| Resource                 | URL                                         | Description       |
| ------------------------ | ------------------------------------------- | ----------------- |
| Stable-Baselines3 Docs   | https://stable-baselines3.readthedocs.io/   | SB3 documentation |
| Stable-Baselines3 GitHub | https://github.com/DLR-RM/stable-baselines3 | SB3 source        |
| Gymnasium Docs           | https://gymnasium.farama.org/               | Gym API docs      |
| PyTorch Tutorials        | https://pytorch.org/tutorials/              | PyTorch learning  |

### Learning Resources

| Resource                 | URL                                             | Description       |
| ------------------------ | ----------------------------------------------- | ----------------- |
| Spinning Up in Deep RL   | https://spinningup.openai.com/                  | OpenAI RL course  |
| Deep RL Bootcamp         | https://sites.google.com/view/deep-rl-bootcamp/ | Berkeley lectures |
| RL Course (David Silver) | https://www.davidsilver.uk/teaching/            | Classic RL course |
| Hugging Face RL Course   | https://huggingface.co/learn/deep-rl-course/    | Modern RL course  |

---

## 🏆 MineRL Competition Solutions

### 2019 Competition

| Place | Team | Approach                | Link |
| ----- | ---- | ----------------------- | ---- |
| 1st   | -    | Behavioral cloning + RL | -    |
| 2nd   | -    | Hierarchical RL         | -    |
| 3rd   | -    | Imitation learning      | -    |

### 2020 Competition

| Place | Team | Approach           | Link |
| ----- | ---- | ------------------ | ---- |
| 1st   | -    | SQIL + fine-tuning | -    |
| 2nd   | -    | BC + PPO           | -    |

### 2021 Competition (BASALT)

| Place | Team | Approach          | Link |
| ----- | ---- | ----------------- | ---- |
| 1st   | -    | VPT-based         | -    |
| 2nd   | -    | Hierarchical + BC | -    |

### Key Insights from Competitions

```
┌─────────────────────────────────────────────────────────────┐
│              COMPETITION INSIGHTS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Imitation Learning Helps                                │
│     └── Pre-training on demonstrations accelerates          │
│         learning significantly                              │
│                                                             │
│  2. Hierarchical Approaches Work Well                       │
│     └── Breaking down into sub-tasks (dig, navigate,        │
│         mine) improves performance                          │
│                                                             │
│  3. Reward Shaping is Critical                              │
│     └── Pure sparse rewards don't work well                 │
│         within competition time limits                      │
│                                                             │
│  4. Action Space Simplification Helps                       │
│     └── Reducing action complexity improves                 │
│         sample efficiency                                   │
│                                                             │
│  5. Visual Representation Matters                           │
│     └── Better CNNs = better policies                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📖 Books

| Book                                    | Authors           | Year | Topics                     |
| --------------------------------------- | ----------------- | ---- | -------------------------- |
| Reinforcement Learning: An Introduction | Sutton & Barto    | 2018 | RL fundamentals            |
| Deep Reinforcement Learning Hands-On    | Lapan             | 2020 | Practical DRL              |
| Grokking Deep Reinforcement Learning    | Morales           | 2020 | Intuitive DRL              |
| Deep Learning                           | Goodfellow et al. | 2016 | Neural network foundations |

---

## 🔧 Tools & Frameworks

### Primary Stack

| Tool              | Version | Purpose       | URL                                         |
| ----------------- | ------- | ------------- | ------------------------------------------- |
| Python            | 3.10    | Language      | https://python.org                          |
| PyTorch           | 2.x     | Deep learning | https://pytorch.org                         |
| Stable-Baselines3 | 2.x     | RL algorithms | https://github.com/DLR-RM/stable-baselines3 |
| MineRL            | 1.0.x   | Environment   | https://minerl.io                           |
| Gymnasium         | 0.29.x  | Env API       | https://gymnasium.farama.org                |

### Supporting Tools

| Tool             | Purpose               | URL                                    |
| ---------------- | --------------------- | -------------------------------------- |
| TensorBoard      | Visualization         | https://www.tensorflow.org/tensorboard |
| Weights & Biases | Experiment tracking   | https://wandb.ai                       |
| Optuna           | Hyperparameter tuning | https://optuna.org                     |
| OpenCV           | Image processing      | https://opencv.org                     |

---

## 📝 Useful Code Repositories

| Repository       | Description        | URL                                         |
| ---------------- | ------------------ | ------------------------------------------- |
| MineRL Baselines | Official baselines | https://github.com/minerllabs/baselines     |
| SB3 Zoo          | Trained agents     | https://github.com/DLR-RM/rl-baselines3-zoo |
| CleanRL          | Single-file RL     | https://github.com/vwxyzjn/cleanrl          |
| RLlib Examples   | Distributed RL     | https://github.com/ray-project/ray          |

---

## 📎 Related Documents

- [RL_ALGORITHMS.md](RL_ALGORITHMS.md)
- [REWARD_DESIGN.md](REWARD_DESIGN.md)
- [../TECH_STACK.md](../TECH_STACK.md)
