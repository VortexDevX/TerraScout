"""
Terra Scout Gymnasium Environment
Wraps the Mineflayer bot as a Gymnasium environment
"""

from typing import Any, Dict, Optional, Tuple, Union

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .client import BridgeClient


class TerraScoutEnv(gym.Env):
    """
    Gymnasium environment for Terra Scout.
    Communicates with Mineflayer bot via HTTP bridge.
    """
    
    metadata = {"render_modes": ["human"]}
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3000,
        max_steps: int = 18000,
        render_mode: Optional[str] = None
    ):
        super().__init__()
        
        self.client = BridgeClient(host, port)
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.current_step = 0
        
        # Action space: discrete actions
        # 0: noop, 1: forward, 2: back, 3: left, 4: right, 
        # 5: jump, 6: forward_jump, 7: dig, 8: look_up, 
        # 9: look_down, 10: look_left, 11: look_right
        self.action_space = spaces.Discrete(12)
        
        # Observation space
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
            1: {"type": "move", "direction": "forward", "duration": 1},
            2: {"type": "move", "direction": "back", "duration": 1},
            3: {"type": "move", "direction": "left", "duration": 1},
            4: {"type": "move", "direction": "right", "duration": 1},
            5: {"type": "jump"},
            6: {"type": "forward_jump"},
            7: {"type": "dig"},
            8: {"type": "look", "pitch": -0.2, "yaw": 0},
            9: {"type": "look", "pitch": 0.2, "yaw": 0},
            10: {"type": "look", "pitch": 0, "yaw": -0.3},
            11: {"type": "look", "pitch": 0, "yaw": 0.3},
        }
    
    def _process_observation(self, raw_obs: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Convert raw observation to gymnasium format."""
        if raw_obs is None:
            return self._empty_observation()
            
        return {
            "position": np.array([
                raw_obs["position"]["x"],
                raw_obs["position"]["y"],
                raw_obs["position"]["z"]
            ], dtype=np.float32),
            "health": np.array([raw_obs["health"]], dtype=np.float32),
            "food": np.array([raw_obs["food"]], dtype=np.float32),
            "yaw": np.array([raw_obs["yaw"]], dtype=np.float32),
            "pitch": np.array([raw_obs["pitch"]], dtype=np.float32),
        }
    
    def _empty_observation(self) -> Dict[str, np.ndarray]:
        """Return empty observation."""
        return {
            "position": np.zeros(3, dtype=np.float32),
            "health": np.array([20.0], dtype=np.float32),
            "food": np.array([20.0], dtype=np.float32),
            "yaw": np.array([0.0], dtype=np.float32),
            "pitch": np.array([0.0], dtype=np.float32),
        }
    
    def _convert_action(self, action: Union[int, np.ndarray, np.integer]) -> int:
        """Convert action to integer."""
        if isinstance(action, np.ndarray):
            return int(action.item())
        elif isinstance(action, np.integer):
            return int(action)
        else:
            return int(action)
    
    def reset(  # type: ignore
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """Reset the environment."""
        super().reset(seed=seed)
        
        self.current_step = 0
        result = self.client.reset()
        
        if "error" in result:
            return self._empty_observation(), {"error": result["error"]}
        
        obs = self._process_observation(result.get("observation"))  # type: ignore
        info = {"raw_observation": result.get("observation")}
        
        return obs, info
    
    def step(
        self,
        action: Union[int, np.ndarray, np.integer]
    ) -> Tuple[Dict[str, np.ndarray], float, bool, bool, Dict[str, Any]]:
        """Execute action in environment."""
        self.current_step += 1
        
        # Convert action to integer
        action_int = self._convert_action(action)
        
        # Map action index to action dict
        action_dict = self.action_map.get(action_int, {"type": "noop"})
        
        # Execute action
        result = self.client.step(action_dict)
        
        if "error" in result:
            return self._empty_observation(), -1.0, True, False, {"error": result["error"]}
        
        obs = self._process_observation(result.get("observation")) # type: ignore
        reward = result.get("reward", 0.0)
        done = result.get("done", False)
        truncated = self.current_step >= self.max_steps
        
        info = {
            "raw_observation": result.get("observation"),
            "step_count": result.get("info", {}).get("stepCount", 0),
            "total_reward": result.get("info", {}).get("totalReward", 0),
        }
        
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