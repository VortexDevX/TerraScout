# 📖 Glossary

> Terms and definitions used throughout the Terra Scout project.

---

## 🎮 Minecraft Terms

| Term            | Definition                                                |
| --------------- | --------------------------------------------------------- |
| **Block**       | The basic unit of the Minecraft world; a 1x1x1 meter cube |
| **Chunk**       | A 16x16x256 block segment of the world                    |
| **Diamond Ore** | Rare ore found at Y-levels -64 to 16; primary target      |
| **Y-Level**     | Vertical coordinate; diamonds spawn below Y=16            |
| **Bedrock**     | Indestructible block at the bottom of the world           |
| **Cave**        | Natural underground opening; common exploration path      |
| **Mob**         | Mobile entity (enemies, animals, NPCs)                    |
| **POV**         | Point of View; first-person camera perspective            |
| **Hotbar**      | Bottom inventory bar with 9 quick-access slots            |
| **Tick**        | Minecraft time unit; 20 ticks = 1 second                  |

---

## 🤖 Reinforcement Learning Terms

| Term                    | Definition                                               |
| ----------------------- | -------------------------------------------------------- |
| **Agent**               | The learning entity that takes actions; Terra Scout      |
| **Environment**         | The world the agent interacts with; Minecraft via MineRL |
| **State (s)**           | Current situation/observation of the agent               |
| **Action (a)**          | Decision made by the agent (move, mine, look)            |
| **Reward (r)**          | Numerical feedback for an action; guides learning        |
| **Policy (π)**          | Strategy mapping states to actions                       |
| **Episode**             | One complete run from start to termination               |
| **Step**                | Single action-observation cycle within an episode        |
| **Trajectory**          | Sequence of states, actions, rewards in an episode       |
| **Return (G)**          | Cumulative reward over an episode                        |
| **Discount Factor (γ)** | Weight for future vs immediate rewards; 0 < γ ≤ 1        |
| **Exploration**         | Trying new actions to discover better strategies         |
| **Exploitation**        | Using known good actions to maximize reward              |
| **ε-greedy**            | Exploration strategy; random action with probability ε   |

---

## 🧠 Deep Learning Terms

| Term                | Definition                                         |
| ------------------- | -------------------------------------------------- |
| **Neural Network**  | Computational model inspired by biological neurons |
| **CNN**             | Convolutional Neural Network; processes images     |
| **MLP**             | Multi-Layer Perceptron; fully connected network    |
| **Forward Pass**    | Computing output from input through the network    |
| **Backpropagation** | Algorithm to compute gradients for learning        |
| **Gradient**        | Direction and magnitude of parameter updates       |
| **Loss Function**   | Measures how wrong predictions are                 |
| **Optimizer**       | Algorithm that updates weights (Adam, SGD)         |
| **Learning Rate**   | Step size for weight updates                       |
| **Batch**           | Group of samples processed together                |
| **Epoch**           | One complete pass through training data            |
| **Overfitting**     | Model memorizes training data; poor generalization |
| **Checkpoint**      | Saved model state for resuming or evaluation       |

---

## 📊 RL Algorithm Terms

| Term                    | Definition                                                  |
| ----------------------- | ----------------------------------------------------------- |
| **PPO**                 | Proximal Policy Optimization; stable policy gradient method |
| **DQN**                 | Deep Q-Network; value-based RL with neural networks         |
| **A2C/A3C**             | Advantage Actor-Critic; policy + value learning             |
| **Value Function V(s)** | Expected return from state s                                |
| **Q-Function Q(s,a)**   | Expected return from state s taking action a                |
| **Advantage A(s,a)**    | Q(s,a) - V(s); how much better action a is                  |
| **Actor**               | Network that outputs actions (policy)                       |
| **Critic**              | Network that estimates value                                |
| **Replay Buffer**       | Storage for past experiences; used in off-policy RL         |
| **On-Policy**           | Learning from current policy's experiences                  |
| **Off-Policy**          | Learning from any policy's experiences                      |

---

## 🎯 Terra Scout Specific Terms

| Term                       | Definition                                           |
| -------------------------- | ---------------------------------------------------- |
| **Terra Scout**            | This project; autonomous Minecraft exploration agent |
| **Diamond Discovery Rate** | Percentage of episodes where diamond is found        |
| **Survival Rate**          | Percentage of episodes where agent doesn't die       |
| **Exploration Efficiency** | Ratio of unique blocks visited to total actions      |
| **Training Run**           | Complete training session with specific config       |
| **Experiment**             | Set of training runs testing a hypothesis            |
| **Baseline**               | Reference performance (e.g., random agent)           |

---

## 🛠️ Technical Terms

| Term                  | Definition                                            |
| --------------------- | ----------------------------------------------------- |
| **MineRL**            | Minecraft Reinforcement Learning environment library  |
| **Gymnasium**         | Standard API for RL environments (formerly Gym)       |
| **Stable-Baselines3** | RL algorithm implementations library                  |
| **PyTorch**           | Deep learning framework                               |
| **CUDA**              | NVIDIA GPU computing platform                         |
| **Tensor**            | Multi-dimensional array; basic PyTorch data structure |
| **YAML**              | Human-readable configuration file format              |
| **Monorepo**          | Single repository containing multiple projects        |
| **ADR**               | Architecture Decision Record                          |
| **CI/CD**             | Continuous Integration / Continuous Deployment        |

---

## 📐 Mathematical Notation

| Symbol | Meaning                                    |
| ------ | ------------------------------------------ |
| s      | State                                      |
| a      | Action                                     |
| r      | Reward                                     |
| π      | Policy                                     |
| θ      | Policy parameters (neural network weights) |
| V(s)   | Value function                             |
| Q(s,a) | Action-value function                      |
| A(s,a) | Advantage function                         |
| γ      | Discount factor                            |
| α      | Learning rate                              |
| ε      | Exploration rate                           |
| τ      | Temperature (for softmax)                  |
| L      | Loss function                              |
| ∇      | Gradient operator                          |
| E[]    | Expected value                             |

---

## 🔗 Abbreviations

| Abbreviation | Full Form                         |
| ------------ | --------------------------------- |
| RL           | Reinforcement Learning            |
| DL           | Deep Learning                     |
| ML           | Machine Learning                  |
| AI           | Artificial Intelligence           |
| API          | Application Programming Interface |
| GPU          | Graphics Processing Unit          |
| CPU          | Central Processing Unit           |
| RAM          | Random Access Memory              |
| VRAM         | Video Random Access Memory        |
| FPS          | Frames Per Second                 |
| MVP          | Minimum Viable Product            |
| PR           | Pull Request                      |
| CI           | Continuous Integration            |

---

## 📎 Related Documents

- [TECH_STACK.md](TECH_STACK.md)
- [research/RL_ALGORITHMS.md](research/RL_ALGORITHMS.md)
