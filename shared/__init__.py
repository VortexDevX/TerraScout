"""
Type definitions for Terra Scout.
"""

from typing import Dict, List, Tuple, Union, Optional, TypedDict, Any
import numpy as np
from numpy.typing import NDArray


# ===========================
# Observation Types
# ===========================

class RawObservation(TypedDict):
    """Raw observation from MineRL environment."""
    pov: NDArray[np.uint8]  # Shape: (H, W, 3)
    inventory: Dict[str, int]
    equipped_items: Dict[str, Any]
    life_stats: Dict[str, float]


class ProcessedObservation(TypedDict):
    """Processed observation ready for neural network."""
    visual: NDArray[np.float32]      # Shape: (C, H, W), normalized
    inventory: NDArray[np.float32]   # Shape: (N,)
    health: NDArray[np.float32]      # Shape: (3,) - life, food, air


# ===========================
# Action Types
# ===========================

class MineRLAction(TypedDict):
    """Full MineRL action format."""
    forward: int
    back: int
    left: int
    right: int
    jump: int
    sneak: int
    sprint: int
    attack: int
    camera: Tuple[float, float]


class SimpleAction(TypedDict):
    """Simplified action format."""
    move: int       # 0=none, 1=forward, 2=back, 3=left, 4=right
    camera: int     # 0=none, 1=up, 2=down, 3=left, 4=right
    action: int     # 0=none, 1=attack, 2=jump


# ===========================
# Experience Types
# ===========================

class Experience(TypedDict):
    """Single step experience for replay."""
    observation: ProcessedObservation
    action: Union[int, NDArray]
    reward: float
    next_observation: ProcessedObservation
    done: bool
    info: Dict[str, Any]


class Episode(TypedDict):
    """Complete episode data."""
    observations: List[ProcessedObservation]
    actions: List[Union[int, NDArray]]
    rewards: List[float]
    dones: List[bool]
    infos: List[Dict[str, Any]]
    total_reward: float
    length: int
    diamond_found: bool


# ===========================
# Configuration Types
# ===========================

class ModelConfig(TypedDict):
    """Model architecture configuration."""
    feature_extractor: Dict[str, Any]
    policy_net: Dict[str, Any]
    value_net: Dict[str, Any]


class TrainingConfig(TypedDict):
    """Training configuration."""
    total_timesteps: int
    learning_rate: float
    batch_size: int
    n_steps: int
    gamma: float
    device: str


# ===========================
# Metrics Types
# ===========================

class EpisodeMetrics(TypedDict):
    """Metrics for a single episode."""
    reward: float
    length: int
    diamond_found: bool
    survived: bool
    final_y_level: float


class TrainingMetrics(TypedDict):
    """Aggregate training metrics."""
    mean_reward: float
    std_reward: float
    diamond_rate: float
    survival_rate: float
    mean_episode_length: float
    policy_loss: float
    value_loss: float
    entropy: float


# ===========================
# Type Aliases
# ===========================

# Tensor types
Tensor = NDArray[np.float32]
ImageTensor = NDArray[np.float32]  # Shape: (C, H, W)
BatchTensor = NDArray[np.float32]  # Shape: (B, ...)

# Coordinate types
Position = Tuple[float, float, float]  # (x, y, z)
BlockPosition = Tuple[int, int, int]   # (x, y, z) integer

# Reward types
Reward = float
RewardDict = Dict[str, float]

# Action types
ActionIndex = int
ActionVector = NDArray[np.float32]