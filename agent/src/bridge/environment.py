"""
Terra Scout Gymnasium Environment
Enhanced with survival and mining actions
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
    Enhanced with survival and smart mining actions.
    """
    
    metadata = {"render_modes": ["human"]}
    
    # Enhanced action set for survival and mining
    ACTION_NAMES = [
        "noop",             # 0: Do nothing
        "forward",          # 1: Move forward
        "back",             # 2: Move backward
        "left",             # 3: Strafe left
        "right",            # 4: Strafe right
        "jump",             # 5: Jump
        "forward_jump",     # 6: Jump forward
        "tunnel_forward",   # 7: Dig 2-high tunnel forward (KEY ACTION)
        "safe_dig_down",    # 8: Safely dig down (checks for lava)
        "dig_forward",      # 9: Dig block in front
        "mine_ore",         # 10: Mine nearest visible ore
        "look_down",        # 11: Look down
        "look_up",          # 12: Look up
        "look_left",        # 13: Turn left
        "look_right",       # 14: Turn right
        "sprint_forward",   # 15: Sprint forward
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
        
        self.use_enhanced_obs = use_enhanced_obs
        self.use_enhanced_rewards = use_enhanced_rewards
        self.obs_processor = ObservationProcessor() if use_enhanced_obs else None
        self.reward_calculator = RewardCalculator() if use_enhanced_rewards else None
        
        self.prev_raw_obs = None
        
        # Action space
        self.action_space = spaces.Discrete(len(self.ACTION_NAMES))
        
        # Observation space (flattened)
        if use_enhanced_obs:
            self.observation_space = spaces.Box(
                low=-np.inf, 
                high=np.inf, 
                shape=(35,),
                dtype=np.float32
            )
        else:
            self.observation_space = spaces.Box(
                low=-np.inf,
                high=np.inf,
                shape=(35,),
                dtype=np.float32
            )
        
        # Action mapping to bot commands
        self.action_map = {
            0: {"type": "noop"},
            1: {"type": "move", "direction": "forward", "duration": 2},
            2: {"type": "move", "direction": "back", "duration": 2},
            3: {"type": "move", "direction": "left", "duration": 2},
            4: {"type": "move", "direction": "right", "duration": 2},
            5: {"type": "jump"},
            6: {"type": "forward_jump"},
            7: {"type": "tunnel_forward"},       # Key mining action
            8: {"type": "safe_dig_down"},        # Safe downward mining
            9: {"type": "dig_forward"},
            10: {"type": "mine_ore"},            # Mine visible ore
            11: {"type": "look", "pitch": 0.4, "yaw": 0},
            12: {"type": "look", "pitch": -0.4, "yaw": 0},
            13: {"type": "look", "pitch": 0, "yaw": -0.5},
            14: {"type": "look", "pitch": 0, "yaw": 0.5},
            15: {"type": "sprint_forward"},
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
        ] + [0.0] * 30, dtype=np.float32)
    
    def _convert_action(self, action: Union[int, np.ndarray, np.integer]) -> int:
        """Convert action to integer."""
        if isinstance(action, np.ndarray):
            return int(action.item())
        elif isinstance(action, np.integer):
            return int(action)
        else:
            return int(action)
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset the environment."""
        super().reset(seed=seed)
        
        self.current_step = 0
        self.prev_raw_obs = None
        
        if self.obs_processor:
            self.obs_processor.reset()
        if self.reward_calculator:
            self.reward_calculator.reset()
        
        result = self.client.reset()
        
        if "error" in result:
            return np.zeros(35, dtype=np.float32), {"error": result["error"]}
        
        raw_obs = result.get("observation")
        self.prev_raw_obs = raw_obs
        
        obs = self._process_observation(raw_obs)
        info = {"raw_observation": raw_obs}
        
        return obs, info
    
    def step(
        self,
        action: Union[int, np.ndarray, np.integer]
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute action in environment."""
        self.current_step += 1
        
        action_int = self._convert_action(action)
        action_dict = self.action_map.get(action_int, {"type": "noop"})
        
        result = self.client.step(action_dict)
        
        if "error" in result:
            return np.zeros(35, dtype=np.float32), -1.0, True, False, {"error": result["error"]}
        
        raw_obs = result.get("observation")
        
        # Calculate reward
        if self.use_enhanced_rewards and self.reward_calculator:
            reward, reward_breakdown = self.reward_calculator.calculate(raw_obs, self.prev_raw_obs)
        else:
            reward = result.get("reward", 0.0)
            reward_breakdown = {}
        
        self.prev_raw_obs = raw_obs
        
        obs = self._process_observation(raw_obs)
        
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
            "mined_ores": result.get("info", {}).get("minedOres", 0),
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


# Register environments
gym.register(
    id="TerraScout-v0",
    entry_point="agent.src.bridge.environment:TerraScoutEnv",
)

gym.register(
    id="TerraScout-v1",
    entry_point="agent.src.bridge.environment:TerraScoutEnv",
    kwargs={"use_enhanced_obs": True, "use_enhanced_rewards": True},
)