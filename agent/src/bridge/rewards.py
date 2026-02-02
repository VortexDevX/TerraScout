"""
Terra Scout Reward Calculator
Diamond-finding focused reward function
"""

from typing import Any, Dict, Optional, Set, Tuple
import numpy as np


class RewardCalculator:
    """
    Calculates rewards for Terra Scout agent.
    Focused on efficient diamond finding.
    """
    
    # Reward values
    REWARDS = {
        # Terminal rewards
        "diamond_found": 1000.0,
        "death": -100.0,
        
        # Y-level rewards
        "enter_diamond_zone": 10.0,      # First time entering Y < 16
        "new_depth_record": 0.5,          # Going deeper than before
        "optimal_y_level": 0.1,           # Being at Y = -59 (optimal)
        
        # Ore discovery
        "diamond_ore_visible": 50.0,      # Seeing diamond ore
        "redstone_ore_visible": 2.0,      # Indicates correct depth
        "other_ore_visible": 0.5,
        
        # Exploration
        "new_block_visited": 0.01,
        "cave_discovered": 1.0,
        
        # Efficiency penalties
        "step_penalty": -0.001,
        "stuck_penalty": -0.1,
        "surface_penalty": -0.01,         # Penalty for being above ground
        
        # Safety penalties
        "damage_taken": -1.0,             # Per health point
        "low_health": -0.5,               # When health < 5
        "danger_proximity": -0.1,         # Near lava
    }
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset for new episode."""
        self.visited_positions: Set[Tuple[int, int, int]] = set()
        self.lowest_y = 320
        self.entered_diamond_zone = False
        self.seen_ores: Set[str] = set()
        self.prev_health = 20
        self.prev_position = None
        self.stuck_counter = 0
        self.total_reward = 0
        self.step_count = 0
    
    def calculate(
        self, 
        observation: Dict[str, Any],
        prev_observation: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate reward for current step.
        
        Args:
            observation: Current observation
            prev_observation: Previous observation
            
        Returns:
            Tuple of (total_reward, reward_breakdown)
        """
        reward = 0.0
        breakdown = {}
        self.step_count += 1
        
        if observation is None:
            return self.REWARDS["step_penalty"], {"step": self.REWARDS["step_penalty"]}
        
        pos = observation.get("position", {"x": 0, "y": 64, "z": 0})
        current_y = pos["y"]
        health = observation.get("health", 20)
        inventory = observation.get("inventory", {})
        nearby_blocks = observation.get("nearbyBlocks", [])
        
        # === Terminal Rewards ===
        
        # Diamond found!
        if inventory.get("diamond", 0) > 0:
            reward += self.REWARDS["diamond_found"]
            breakdown["diamond_found"] = self.REWARDS["diamond_found"]
            return reward, breakdown
        
        # Death
        if health <= 0:
            reward += self.REWARDS["death"]
            breakdown["death"] = self.REWARDS["death"]
            return reward, breakdown
        
        # === Step Penalty ===
        reward += self.REWARDS["step_penalty"]
        breakdown["step"] = self.REWARDS["step_penalty"]
        
        # === Y-Level Rewards ===
        
        # First time entering diamond zone
        if current_y <= 16 and not self.entered_diamond_zone:
            reward += self.REWARDS["enter_diamond_zone"]
            breakdown["enter_diamond_zone"] = self.REWARDS["enter_diamond_zone"]
            self.entered_diamond_zone = True
        
        # New depth record
        if current_y < self.lowest_y:
            depth_bonus = self.REWARDS["new_depth_record"] * (self.lowest_y - current_y)
            reward += depth_bonus
            breakdown["new_depth"] = depth_bonus
            self.lowest_y = current_y
        
        # Optimal Y-level bonus
        if -64 <= current_y <= -50:
            reward += self.REWARDS["optimal_y_level"]
            breakdown["optimal_y"] = self.REWARDS["optimal_y_level"]
        
        # Surface penalty (discourages staying above ground)
        if current_y > 62:
            reward += self.REWARDS["surface_penalty"]
            breakdown["surface_penalty"] = self.REWARDS["surface_penalty"]
        
        # === Ore Discovery ===
        for block in nearby_blocks:
            name = block.get("name", "")
            ore_key = f"{name}_{block.get('position', {})}"
            
            if ore_key not in self.seen_ores:
                if "diamond_ore" in name:
                    reward += self.REWARDS["diamond_ore_visible"]
                    breakdown["diamond_ore_visible"] = self.REWARDS["diamond_ore_visible"]
                    self.seen_ores.add(ore_key)
                elif "redstone_ore" in name:
                    reward += self.REWARDS["redstone_ore_visible"]
                    breakdown["redstone_visible"] = breakdown.get("redstone_visible", 0) + self.REWARDS["redstone_ore_visible"]
                    self.seen_ores.add(ore_key)
                elif "_ore" in name:
                    reward += self.REWARDS["other_ore_visible"]
                    breakdown["other_ore"] = breakdown.get("other_ore", 0) + self.REWARDS["other_ore_visible"]
                    self.seen_ores.add(ore_key)
        
        # === Exploration ===
        block_pos = (int(pos["x"]), int(pos["y"]), int(pos["z"]))
        if block_pos not in self.visited_positions:
            reward += self.REWARDS["new_block_visited"]
            breakdown["exploration"] = self.REWARDS["new_block_visited"]
            self.visited_positions.add(block_pos)
        
        # Stuck detection
        if self.prev_position is not None:
            dist = np.sqrt(
                (pos["x"] - self.prev_position["x"])**2 +
                (pos["y"] - self.prev_position["y"])**2 +
                (pos["z"] - self.prev_position["z"])**2
            )
            if dist < 0.1:
                self.stuck_counter += 1
                if self.stuck_counter > 10:
                    reward += self.REWARDS["stuck_penalty"]
                    breakdown["stuck"] = self.REWARDS["stuck_penalty"]
            else:
                self.stuck_counter = 0
        
        self.prev_position = pos
        
        # === Health/Safety ===
        
        # Damage taken
        if health < self.prev_health:
            damage = self.prev_health - health
            damage_penalty = self.REWARDS["damage_taken"] * damage
            reward += damage_penalty
            breakdown["damage"] = damage_penalty
        self.prev_health = health
        
        # Low health warning
        if health < 5:
            reward += self.REWARDS["low_health"]
            breakdown["low_health"] = self.REWARDS["low_health"]
        
        # Danger proximity (lava)
        for block in nearby_blocks:
            if block.get("name") in ("lava", "flowing_lava"):
                reward += self.REWARDS["danger_proximity"]
                breakdown["danger"] = self.REWARDS["danger_proximity"]
                break
        
        self.total_reward += reward
        return reward, breakdown
    
    def get_stats(self) -> Dict[str, Any]:
        """Get episode statistics."""
        return {
            "total_reward": self.total_reward,
            "steps": self.step_count,
            "lowest_y": self.lowest_y,
            "blocks_visited": len(self.visited_positions),
            "ores_found": len(self.seen_ores),
            "entered_diamond_zone": self.entered_diamond_zone,
        }