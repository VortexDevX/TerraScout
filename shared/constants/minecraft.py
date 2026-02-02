"""
Minecraft-specific constants for Terra Scout.
"""

# ===========================
# World Generation
# ===========================

# Y-level ranges (1.18+ world generation)
WORLD_MIN_Y = -64
WORLD_MAX_Y = 320
SEA_LEVEL = 62
BEDROCK_LAYER = -64

# Diamond ore spawn range
DIAMOND_Y_MIN = -64
DIAMOND_Y_MAX = 16
DIAMOND_OPTIMAL_Y = -59  # Highest concentration

# Other ore ranges
ORE_RANGES = {
    "coal": (-64, 192),
    "iron": (-64, 72),
    "gold": (-64, 32),
    "redstone": (-64, 16),
    "lapis": (-64, 64),
    "diamond": (-64, 16),
    "emerald": (-16, 320),  # Mountains only
}

# ===========================
# Block IDs
# ===========================

BLOCK_IDS = {
    "air": 0,
    "stone": 1,
    "dirt": 3,
    "cobblestone": 4,
    "bedrock": 7,
    "water": 9,
    "lava": 11,
    "sand": 12,
    "gravel": 13,
    "coal_ore": 16,
    "iron_ore": 15,
    "gold_ore": 14,
    "diamond_ore": 56,
    "redstone_ore": 73,
    "lapis_ore": 21,
    "obsidian": 49,
}

# Dangerous blocks
DANGEROUS_BLOCKS = {
    "lava": 11,
    "fire": 51,
    "cactus": 81,
}

# Valuable ores
VALUABLE_ORES = {
    "diamond_ore": 56,
    "gold_ore": 14,
    "iron_ore": 15,
    "redstone_ore": 73,
    "lapis_ore": 21,
    "coal_ore": 16,
}

# ===========================
# Actions
# ===========================

ACTION_KEYS = [
    "forward",
    "back",
    "left",
    "right",
    "jump",
    "sneak",
    "sprint",
    "attack",
    "camera",
]

# Simplified action space
SIMPLE_ACTIONS = {
    "noop": 0,
    "forward": 1,
    "back": 2,
    "left": 3,
    "right": 4,
    "jump": 5,
    "attack": 6,
    "forward_jump": 7,
    "forward_attack": 8,
}

# Camera movement discretization
CAMERA_ANGLES = {
    "look_up": (-15, 0),
    "look_down": (15, 0),
    "look_left": (0, -15),
    "look_right": (0, 15),
    "look_up_left": (-15, -15),
    "look_up_right": (-15, 15),
    "look_down_left": (15, -15),
    "look_down_right": (15, 15),
}

# ===========================
# Game Mechanics
# ===========================

# Ticks
TICKS_PER_SECOND = 20
SECONDS_PER_MINUTE = 60
TICKS_PER_MINUTE = TICKS_PER_SECOND * SECONDS_PER_MINUTE

# Health and hunger
MAX_HEALTH = 20.0
MAX_FOOD = 20.0
MAX_AIR = 300.0

# Fall damage
SAFE_FALL_DISTANCE = 3
FATAL_FALL_DISTANCE = 23

# Tool durability
WOOD_PICKAXE_DURABILITY = 59
STONE_PICKAXE_DURABILITY = 131
IRON_PICKAXE_DURABILITY = 250
DIAMOND_PICKAXE_DURABILITY = 1561

# ===========================
# Environment
# ===========================

# Default episode settings
DEFAULT_MAX_STEPS = 18000  # ~15 minutes
DEFAULT_INVENTORY_SLOTS = 36

# Observation dimensions
POV_WIDTH = 64
POV_HEIGHT = 64
POV_CHANNELS = 3