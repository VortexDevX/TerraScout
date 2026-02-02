"""
Terra Scout Bridge Module
Provides communication between Python agent and Mineflayer bot
"""

from .client import BridgeClient, AsyncBridgeClient
from .environment import TerraScoutEnv
from .observations import ObservationProcessor
from .rewards import RewardCalculator

__all__ = [
    "BridgeClient", 
    "AsyncBridgeClient", 
    "TerraScoutEnv",
    "ObservationProcessor",
    "RewardCalculator",
]