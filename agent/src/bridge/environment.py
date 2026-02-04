"""
Terra Scout Gymnasium Environment
Phase 6: Smart Diamond Hunting System
"""

from typing import Any, Dict, Optional, Tuple, Union
import random

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .client import BridgeClient
from .observations import ObservationProcessor
from .rewards import RewardCalculator


class TerraScoutEnv(gym.Env):
    """Enhanced environment with smart diamond hunting system."""
    
    metadata = {"render_modes": ["human"]}
    
    # Action set optimized for diamond mining
    ACTION_NAMES = [
        "noop",             # 0
        "forward",          # 1
        "back",             # 2
        "left",             # 3
        "right",            # 4
        "jump",             # 5
        "forward_jump",     # 6
        "descend",          # 7 - Staircase down to diamond level
        "strip_mine",       # 8 - Strip mining pattern
        "branch_mine",      # 9 - Branch mining with side tunnels
        "tunnel_forward",   # 10 - Dig 2-high tunnel
        "mine_ore",         # 11 - Mine nearest visible ore
        "mine_diamond",     # 12 - Priority: mine diamond ore specifically
        "explore_cave",     # 13 - Follow cave system
        "find_cave",        # 14 - Look for cave entrance
        "safe_dig_down",    # 15 - Safe dig with lava check
        "look_down",        # 16
        "look_up",          # 17
        "look_left",        # 18
        "look_right",       # 19
        "switch_direction", # 20 - Change mining direction
    ]
    
    # Mining actions for biasing at optimal depth
    MINING_ACTIONS = [7, 8, 9, 10, 11, 12]  # descend, strip, branch, tunnel, ore, diamond
    MINE_DIAMOND_ACTION = 12
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3000,
        max_steps: int = 18000,
        render_mode: Optional[str] = None,
        use_enhanced_obs: bool = True,
        use_enhanced_rewards: bool = True,
        smart_action_bias: bool = True,  # NEW: Enable smart action selection
    ):
        super().__init__()
        
        self.client = BridgeClient(host, port)
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.current_step = 0
        self.smart_action_bias = smart_action_bias
        
        self.use_enhanced_obs = use_enhanced_obs
        self.use_enhanced_rewards = use_enhanced_rewards
        self.obs_processor = ObservationProcessor() if use_enhanced_obs else None
        self.reward_calculator = RewardCalculator() if use_enhanced_rewards else None
        
        self.prev_raw_obs = None
        self.current_y = 64  # Track current Y level
        self.diamond_nearby = False  # Track diamond visibility
        
        # Action and observation spaces
        self.action_space = spaces.Discrete(len(self.ACTION_NAMES))
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(35,), dtype=np.float32
        )
        
        # Action mapping
        self.action_map = {i: {"type": name} for i, name in enumerate(self.ACTION_NAMES)}
    
    def _smart_action_override(self, action: int) -> int:
        """
        SMART ACTION SYSTEM:
        1. If diamond is visible -> FORCE mine_diamond action
        2. If at optimal depth -> 50% chance to bias toward mining actions
        """
        if not self.smart_action_bias:
            return action
        
        # RULE 1: Diamond visible = MUST mine diamond
        if self.diamond_nearby:
            return self.MINE_DIAMOND_ACTION
        
        # RULE 2: At optimal depth (-59 to -50), bias toward mining
        if -59 <= self.current_y <= -45:
            # 50% chance to override with a mining action
            if random.random() < 0.5:
                return random.choice(self.MINING_ACTIONS)
        
        # RULE 3: Above surface, encourage descending
        if self.current_y > 0:
            if random.random() < 0.3:
                return 7  # descend action
        
        return action
    
    def _process_observation(self, raw_obs: Dict[str, Any]) -> np.ndarray:
        if raw_obs is None:
            return np.zeros(35, dtype=np.float32)
        
        # Update state for smart action selection
        pos = raw_obs.get("position", {})
        self.current_y = pos.get("y", 64)
        self.diamond_nearby = raw_obs.get("diamondNearby", False)
        
        if self.use_enhanced_obs and self.obs_processor:
            return self.obs_processor.get_flat_observation(raw_obs)
        
        # Simple fallback
        return np.array([
            pos.get("x", 0) / 1000.0, pos.get("y", 64) / 320.0, pos.get("z", 0) / 1000.0,
            raw_obs.get("health", 20) / 20.0,
            raw_obs.get("food", 20) / 20.0,
            float(raw_obs.get("inCave", False)),
            float(raw_obs.get("atDiamondLevel", False)),
            float(raw_obs.get("diamondNearby", False)),
        ] + [0.0] * 27, dtype=np.float32)
    
    def _convert_action(self, action: Union[int, np.ndarray, np.integer]) -> int:
        if isinstance(action, np.ndarray):
            return int(action.item())
        return int(action)
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None): # type: ignore
        super().reset(seed=seed)
        
        self.current_step = 0
        self.prev_raw_obs = None
        self.current_y = 64
        self.diamond_nearby = False
        
        if self.obs_processor:
            self.obs_processor.reset()
        if self.reward_calculator:
            self.reward_calculator.reset()
        
        result = self.client.reset()
        
        if "error" in result:
            return np.zeros(35, dtype=np.float32), {"error": result["error"]}
        
        raw_obs = result.get("observation")
        self.prev_raw_obs = raw_obs
        
        return self._process_observation(raw_obs), {"raw_observation": raw_obs}  # type: ignore
    
    def step(self, action):
        self.current_step += 1
        
        action_int = self._convert_action(action)
        
        # SMART ACTION OVERRIDE
        original_action = action_int
        action_int = self._smart_action_override(action_int)
        was_overridden = action_int != original_action
        
        action_dict = self.action_map.get(action_int, {"type": "noop"})
        
        result = self.client.step(action_dict)
        
        if "error" in result:
            return np.zeros(35, dtype=np.float32), -1.0, True, False, {"error": result["error"]}
        
        raw_obs = result.get("observation")
        
        if self.use_enhanced_rewards and self.reward_calculator:
            reward, breakdown = self.reward_calculator.calculate(raw_obs, self.prev_raw_obs)  # type: ignore
        else:
            reward = result.get("reward", 0.0)
            breakdown = {}
        
        self.prev_raw_obs = raw_obs
        
        obs = self._process_observation(raw_obs) # type: ignore
        done = result.get("done", False)
        truncated = self.current_step >= self.max_steps
        
        # Diamond check
        if raw_obs and raw_obs.get("diamondsThisEpisode", 0) > 0:
            done = True
        
        info = {
            "raw_observation": raw_obs,
            "step_count": self.current_step,
            "action_name": self.ACTION_NAMES[action_int],
            "action_overridden": was_overridden,
            "reward_breakdown": breakdown,
            "strategy": raw_obs.get("currentStrategy", "unknown") if raw_obs else "unknown",
            "in_cave": raw_obs.get("inCave", False) if raw_obs else False,
            "diamond_nearby": self.diamond_nearby,
            "current_y": self.current_y,
        }
        
        if self.reward_calculator:
            info["episode_stats"] = self.reward_calculator.get_stats()
        
        return obs, reward, done, truncated, info
    
    def render(self):
        pass
    
    def close(self):
        self.client.close()


# Register
gym.register(id="TerraScout-v0", entry_point="agent.src.bridge.environment:TerraScoutEnv")
gym.register(id="TerraScout-v2", entry_point="agent.src.bridge.environment:TerraScoutEnv",
             kwargs={"use_enhanced_obs": True, "use_enhanced_rewards": True})
gym.register(id="TerraScout-v3", entry_point="agent.src.bridge.environment:TerraScoutEnv",
             kwargs={"use_enhanced_obs": True, "use_enhanced_rewards": True, "smart_action_bias": True})
