# 📋 Project Scope

> Defining what Terra Scout is, what it does, and what it doesn't do.

---

## 🎯 Project Definition

**Terra Scout** is an autonomous reinforcement learning agent that explores Minecraft environments to locate diamond ore efficiently with minimal human intervention.

---

## ✅ In Scope

### Core Functionality

| Feature                  | Description                          | Priority      |
| ------------------------ | ------------------------------------ | ------------- |
| Autonomous Exploration   | Agent navigates without human input  | P0 (Critical) |
| Diamond Detection        | Locate and identify diamond ore      | P0 (Critical) |
| Environment Observation  | Process visual/state information     | P0 (Critical) |
| Decision Making          | Select optimal actions via RL policy | P0 (Critical) |
| Learning from Experience | Improve strategy over training       | P0 (Critical) |
| Risk Avoidance           | Minimize damage/death                | P1 (High)     |
| Efficiency Optimization  | Reduce time/actions to find diamonds | P1 (High)     |

### Technical Scope

| Component                             | Included |
| ------------------------------------- | -------- |
| MineRL environment integration        | ✅       |
| Custom reward function design         | ✅       |
| RL algorithm implementation (PPO/DQN) | ✅       |
| Training pipeline (local + Kaggle)    | ✅       |
| Model checkpointing and versioning    | ✅       |
| Basic evaluation metrics              | ✅       |
| Documentation                         | ✅       |

### Environment Scope

| Environment Aspect                 | Included |
| ---------------------------------- | -------- |
| Underground exploration            | ✅       |
| Cave navigation                    | ✅       |
| Basic terrain traversal            | ✅       |
| Ore identification                 | ✅       |
| Survival mechanics (health/damage) | ✅       |

---

## ❌ Out of Scope

### Explicitly Excluded (MVP)

| Feature                 | Reason                                |
| ----------------------- | ------------------------------------- |
| Building structures     | Not relevant to exploration goal      |
| Combat / Fighting mobs  | Adds complexity, not core objective   |
| Crafting items          | Beyond exploration scope              |
| Inventory management    | Minimal relevance for diamond finding |
| Multiplayer interaction | Single-agent focus                    |
| Surface exploration     | Diamond focus = underground priority  |
| Multiple resource types | MVP focuses on diamonds only          |
| Real-time web dashboard | Post-MVP feature                      |
| API backend             | Post-MVP feature                      |

### Technical Exclusions (MVP)

| Component                | Status   |
| ------------------------ | -------- |
| Distributed training     | Post-MVP |
| Model serving/deployment | Post-MVP |
| A/B testing framework    | Post-MVP |
| Production monitoring    | Post-MVP |

---

## 🎯 Success Criteria

### Primary Metrics

| Metric                  | Target            | Measurement                      |
| ----------------------- | ----------------- | -------------------------------- |
| Diamond Discovery Rate  | > 60% of episodes | Episodes where diamond is found  |
| Average Time to Diamond | < 5 minutes       | Steps/time from spawn to diamond |
| Survival Rate           | > 70%             | Episodes without agent death     |
| Learning Improvement    | Measurable        | Compare early vs late training   |

### Secondary Metrics

| Metric               | Target                              |
| -------------------- | ----------------------------------- |
| Action Efficiency    | Fewer redundant actions over time   |
| Exploration Coverage | More unique blocks visited          |
| Consistency          | Low variance across different seeds |

---

## 📅 Milestones

| Milestone | Description                              | Phase      |
| --------- | ---------------------------------------- | ---------- |
| M0        | Project structure and documentation      | Phase 0 ✅ |
| M1        | MineRL environment running locally       | Phase 1    |
| M2        | Basic agent interacting with environment | Phase 2    |
| M3        | Training pipeline functional             | Phase 3    |
| M4        | Agent finds diamonds (any efficiency)    |
