"""
Terra Scout Gymnasium Environment
Enhanced version with better observations and rewards
"""

from typing import Any, Dict, Optional, Tuple, Union

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .client import BridgeClient
from .observations import ObservationProcessor
from .rewards import RewardCalculator


class TerraScoutEnv(gym.Env):
    """
    Gymnasium environment for Terra Scout.
    Communicates with Mineflayer bot via HTTP bridge.
    """
    
    metadata = {"render_modes": ["human"]}
    
    # Action definitions
    ACTION_NAMES = [
        "noop",          # 0
        "forward",       # 1
        "back",          # 2
        "left",          # 3
        "right",         # 4
        "jump",          # 5
        "forward_jump",  # 6
        "dig",           # 7
        "dig_down",      # 8
        "look_up",       # 9
        "look_down",     # 10
        "look_left",     # 11
        "look_right",    # 12
        "sprint_forward",# 13
    ]
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3000,
        max_steps: int = 18000,
        render_mode: Optional[str] = None,
        use_enhanced_obs: bool = True,
        use_enhanced_rewards: bool = True,
    ):
        super().__init__()
        
        self.client = BridgeClient(host, port)
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.current_step = 0
        
        # Enhanced processing
        self.use_enhanced_obs = use_enhanced_obs
        self.use_enhanced_rewards = use_enhanced_rewards
        self.obs_processor = ObservationProcessor() if use_enhanced_obs else None
        self.reward_calculator = RewardCalculator() if use_enhanced_rewards else None
        
        self.prev_raw_obs = None
        
        # Action space
        self.action_space = spaces.Discrete(len(self.ACTION_NAMES))
        
        # Observation space
        if use_enhanced_obs:
            self.observation_space = spaces.Box(
                low=-np.inf, 
                high=np.inf, 
                shape=(35,),  # Flattened observation size
                dtype=np.float32
            )
        else:
            self.observation_space = spaces.Dict({
                "position": spaces.Box(low=-1e6, high=1e6, shape=(3,), dtype=np.float32),
                "health": spaces.Box(low=0, high=20, shape=(1,), dtype=np.float32),
                "food": spaces.Box(low=0, high=20, shape=(1,), dtype=np.float32),
                "yaw": spaces.Box(low=-np.pi, high=np.pi, shape=(1,), dtype=np.float32),
                "pitch": spaces.Box(low=-np.pi/2, high=np.pi/2, shape=(1,), dtype=np.float32),
            })
        
        # Action mapping
        self.action_map = {
            0: {"type": "noop"},
            1: {"type": "move", "direction": "forward", "duration": 2},
            2: {"type": "move", "direction": "back", "duration": 2},
            3: {"type": "move", "direction": "left", "duration": 2},
            4: {"type": "move", "direction": "right", "duration": 2},
            5: {"type": "jump"},
            6: {"type": "forward_jump"},
            7: {"type": "dig"},
            8: {"type": "dig_down"},
            9: {"type": "look", "pitch": -0.3, "yaw": 0},
            10: {"type": "look", "pitch": 0.3, "yaw": 0},
            11: {"type": "look", "pitch": 0, "yaw": -0.4},
            12: {"type": "look", "pitch": 0, "yaw": 0.4},
            13: {"type": "sprint_forward"},
        }
    
    def _process_observation(self, raw_obs: Dict[str, Any]) -> np.ndarray:
        """Convert raw observation to numpy array."""
        if raw_obs is None:
            return np.zeros(35, dtype=np.float32)
        
        if self.use_enhanced_obs and self.obs_processor:
            return self.obs_processor.get_flat_observation(raw_obs)
        else:
            return self._simple_observation(raw_obs)
    
    def _simple_observation(self, raw_obs: Dict[str, Any]) -> np.ndarray:
        """Simple observation processing."""
        pos = raw_obs.get("position", {"x": 0, "y": 64, "z": 0})
        return np.array([
            pos["x"] / 1000.0,
            pos["y"] / 320.0,
            pos["z"] / 1000.0,
            raw_obs.get("health", 20) / 20.0,
            raw_obs.get("food", 20) / 20.0,
        ] + [0.0] * 30, dtype=np.float32)  # Pad to 35
    
    def _convert_action(self, action: Union[int, np.ndarray, np.integer]) -> int:
        """Convert action to integer."""
        if isinstance(action, np.ndarray):
            return int(action.item())
        elif isinstance(action, np.integer):
            return int(action)
        else:
            return int(action)
    
    def reset( # type: ignore
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset the environment."""
        super().reset(seed=seed)
        
        self.current_step = 0
        self.prev_raw_obs = None
        
        # Reset processors
        if self.obs_processor:
            self.obs_processor.reset()
        if self.reward_calculator:
            self.reward_calculator.reset()
        
        # Reset bot
        result = self.client.reset()
        
        if "error" in result:
            return np.zeros(35, dtype=np.float32), {"error": result["error"]}
        
        raw_obs = result.get("observation")
        self.prev_raw_obs = raw_obs
        
        obs = self._process_observation(raw_obs) # type: ignore
        info = {"raw_observation": raw_obs}
        
        return obs, info
    
    def step(
        self,
        action: Union[int, np.ndarray, np.integer]
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute action in environment."""
        self.current_step += 1
        
        # Convert action to integer
        action_int = self._convert_action(action)
        
        # Map action index to action dict
        action_dict = self.action_map.get(action_int, {"type": "noop"})
        
        # Execute action
        result = self.client.step(action_dict)
        
        if "error" in result:
            return np.zeros(35, dtype=np.float32), -1.0, True, False, {"error": result["error"]}
        
        raw_obs = result.get("observation")
        
        # Calculate reward
        if self.use_enhanced_rewards and self.reward_calculator:
            reward, reward_breakdown = self.reward_calculator.calculate(raw_obs, self.prev_raw_obs) # type: ignore
        else:
            reward = result.get("reward", 0.0)
            reward_breakdown = {}
        
        self.prev_raw_obs = raw_obs
        
        # Process observation
        obs = self._process_observation(raw_obs) # type: ignore
        
        # Check termination
        done = result.get("done", False)
        truncated = self.current_step >= self.max_steps
        
        # Check for diamond
        if raw_obs and raw_obs.get("inventory", {}).get("diamond", 0) > 0:
            done = True
        
        info = {
            "raw_observation": raw_obs,
            "step_count": self.current_step,
            "action_name": self.ACTION_NAMES[action_int],
            "reward_breakdown": reward_breakdown,
        }
        
        if self.reward_calculator:
            info["episode_stats"] = self.reward_calculator.get_stats()
        
        return obs, reward, done, truncated, info
    
    def render(self):
        """Render is handled by Minecraft client."""
        pass
    
    def close(self):
        """Close the environment."""
        self.client.close()


# Register the environment
gym.register(
    id="TerraScout-v0",
    entry_point="agent.src.bridge.environment:TerraScoutEnv",
)

gym.register(
    id="TerraScout-v1",
    entry_point="agent.src.bridge.environment:TerraScoutEnv",
    kwargs={"use_enhanced_obs": True, "use_enhanced_rewards": True},
)