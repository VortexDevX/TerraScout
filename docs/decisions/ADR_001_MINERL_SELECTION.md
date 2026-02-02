# ADR 001: MineRL Selection

> Architecture Decision Record for choosing MineRL as the Minecraft RL environment.

---

## 📋 Metadata

| Field         | Value            |
| ------------- | ---------------- |
| **ID**        | ADR-001          |
| **Title**     | MineRL Selection |
| **Status**    | ✅ Accepted      |
| **Date**      | 2025-01-XX       |
| **Author**    | VortexDevX       |
| **Reviewers** | -                |

---

## 🎯 Context

Terra Scout requires a Minecraft environment interface to:

- Observe the game state (visual + inventory)
- Execute actions (movement, mining, camera)
- Receive feedback for reinforcement learning
- Support training on GPU infrastructure

### Options Considered

| Option              | Description                               |
| ------------------- | ----------------------------------------- |
| **Project Malmo**   | Microsoft's Minecraft AI platform         |
| **MineRL**          | OpenAI Gym-based Minecraft RL environment |
| **Mineflayer**      | JavaScript-based Minecraft bot framework  |
| **Custom Solution** | Build interface from scratch              |

---

## 🔍 Analysis

### Project Malmo

| Aspect                 | Assessment                                            |
| ---------------------- | ----------------------------------------------------- |
| **Pros**               | Feature-rich, Microsoft-backed, flexible              |
| **Cons**               | Abandoned (~2020), Python 3.6-3.7 only, complex setup |
| **Python Support**     | ❌ 3.6-3.7 (EOL)                                      |
| **Active Development** | ❌ No                                                 |
| **Community**          | ❌ Minimal                                            |
| **Windows 11**         | ⚠️ Problematic                                        |

### MineRL

| Aspect                 | Assessment                                                             |
| ---------------------- | ---------------------------------------------------------------------- |
| **Pros**               | Gymnasium API, active community, RL-focused, pretrained data available |
| **Cons**               | Java path issues on Windows, wheel build can fail                      |
| **Python Support**     | ✅ 3.8-3.10                                                            |
| **Active Development** | ✅ Yes (2023)                                                          |
| **Community**          | ✅ Active RL research community                                        |
| **Windows 11**         | ✅ Workable with proper setup                                          |

### Mineflayer

| Aspect             | Assessment                                                       |
| ------------------ | ---------------------------------------------------------------- |
| **Pros**           | Very active, large community, flexible                           |
| **Cons**           | JavaScript-based, not designed for RL, requires bridge to Python |
| **Python Support** | ❌ N/A (JavaScript)                                              |
| **RL Integration** | ❌ Manual implementation required                                |

### Custom Solution

| Aspect            | Assessment                                        |
| ----------------- | ------------------------------------------------- |
| **Pros**          | Full control, tailored to needs                   |
| **Cons**          | Massive development effort, reinventing the wheel |
| **Time Required** | ❌ Months of work                                 |
| **Feasibility**   | ❌ Not practical for solo project                 |

---

## ✅ Decision

**Selected: MineRL**

### Rationale

1. **Gymnasium Compatibility**
   - Standard RL interface (reset, step, render)
   - Works with Stable-Baselines3 out of the box
   - Familiar API for RL practitioners

2. **Active Maintenance**
   - Updates as recent as 2023
   - Bug fixes and improvements ongoing
   - Responsive to issues

3. **Python 3.10 Support**
   - Modern Python version
   - Compatible with latest ML libraries
   - Not locked to EOL Python

4. **RL Research Focus**
   - Built specifically for RL research
   - MineRL competition datasets available
   - Reward shaping research available

5. **Known Issues are Solvable**
   - Java path: Set JAVA_HOME correctly
   - Wheel build: Install Visual C++ Build Tools
   - Both have documented solutions

---

## 🔧 Implementation Notes

### Prerequisites

```powershell
# Verify Java 8
java -version  # Should show 1.8.x

# Set JAVA_HOME (if not set)
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Java\jdk1.8.0_XXX', 'User')

# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Installation

```bash
pip install minerl
```

### Verification

```python
import minerl
import gymnasium as gym

env = gym.make('MineRLNavigateDense-v0')
obs, info = env.reset()
print("MineRL working!")
env.close()
```

---

## 📊 Consequences

### Positive

- ✅ Standard RL workflow
- ✅ SB3 integration
- ✅ Modern Python
- ✅ Community support
- ✅ Research resources available

### Negative

- ⚠️ Windows setup requires care
- ⚠️ Java 8 specifically required
- ⚠️ Large download (Minecraft assets)
- ⚠️ Can be slow to initialize

### Neutral

- Environment locked to specific Minecraft version
- Must work within MineRL's observation/action space

---

## 🔄 Review Triggers

This decision should be revisited if:

- MineRL becomes unmaintained
- A superior alternative emerges
- Critical bugs are discovered with no fixes
- Python 3.10 becomes EOL

---

## 📎 Related Documents

- [../TECH_STACK.md](../TECH_STACK.md)
- [../guides/SETUP_GUIDE.md](../guides/SETUP_GUIDE.md)
- [../guides/TROUBLESHOOTING.md](../guides/TROUBLESHOOTING.md)
