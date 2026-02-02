"""
Reward constants for Terra Scout.
"""

# ===========================
# Terminal Rewards
# ===========================

# Primary objective
DIAMOND_FOUND_REWARD = 1000.0

# Failure states
DEATH_PENALTY = -100.0
TIMEOUT_PENALTY = -10.0

# ===========================
# Progress Rewards
# ===========================

# Y-level progress
Y_LEVEL_REWARD_MULTIPLIER = 0.1
ENTER_DIAMOND_ZONE_BONUS = 5.0
DEEP_DIAMOND_ZONE_BONUS = 10.0

# Exploration
NEW_BLOCK_EXPLORED_REWARD = 0.05
CAVE_DISCOVERED_REWARD = 0.5

# ===========================
# Ore Discovery Rewards
# ===========================

ORE_REWARDS = {
    "diamond_ore": 50.0,    # Seeing diamond (not mining)
    "redstone_ore": 3.0,    # Indicates correct Y-level
    "lapis_ore": 2.5,       # Indicates correct Y-level
    "gold_ore": 1.5,        # Underground indicator
    "iron_ore": 1.0,        # Common underground
    "coal_ore": 0.5,        # Very common
}

# ===========================
# Penalties
# ===========================

# Efficiency penalties
STEP_PENALTY = -0.001
LARGE_STEP_PENALTY = -0.01

# Behavior penalties
STUCK_PENALTY = -0.1
REPEATED_ACTION_PENALTY = -0.05
INVALID_ACTION_PENALTY = -0.01

# Safety penalties
DAMAGE_TAKEN_MULTIPLIER = -1.0  # Per health point lost
LOW_HEALTH_PENALTY = -0.5       # When health < 5
DANGER_PROXIMITY_PENALTY = -0.1 # Near lava/void

# ===========================
# Reward Bounds
# ===========================

# For normalization
REWARD_CLIP_MIN = -100.0
REWARD_CLIP_MAX = 1000.0

# Running normalization
REWARD_NORM_EPSILON = 1e-8

# ===========================
# Reward Shaping Parameters
# ===========================

# Shaping decay schedule
SHAPING_START_WEIGHT = 1.0
SHAPING_END_WEIGHT = 0.0
SHAPING_DECAY_EPISODES = 150000

# Curiosity bonus
CURIOSITY_SCALE = 0.1
CURIOSITY_DECAY = 0.999

# ===========================
# Achievement Rewards
# ===========================

# One-time bonuses
FIRST_ORE_BONUS = 2.0
FIRST_UNDERGROUND_BONUS = 1.0
FIRST_CAVE_BONUS = 3.0
REACHED_DIAMOND_LEVEL_BONUS = 10.0

# ===========================
# Auxiliary Signals
# ===========================

# For debugging/analysis (not used in training)
INFO_REWARDS = {
    "diamond_rate": "Diamond discovery rate",
    "survival_rate": "Episode survival rate",
    "exploration_efficiency": "Unique blocks / total steps",
    "depth_progress": "Average Y-level decrease",
}