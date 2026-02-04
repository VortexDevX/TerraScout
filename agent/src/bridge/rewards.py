"""
Terra Scout Reward Calculator
Enhanced for survival and mining
"""

from typing import Any, Dict, Optional, Set, Tuple
import numpy as np


class RewardCalculator:
    """
    Calculates rewards for Terra Scout agent.
    Enhanced for survival and actual ore mining.
    """
    
    REWARDS = {
        # Terminal rewards
        "diamond_found": 1000.0,
        "death": -100.0,
        
        # Mining rewards - INCREASED to encourage actual mining
        "mined_diamond_ore": 200.0,  # Was 100 - doubled!
        "mined_iron_ore": 5.0,
        "mined_gold_ore": 10.0,
        "mined_redstone_ore": 8.0,
        "mined_other_ore": 2.0,
        
        # Y-level rewards
        "enter_diamond_zone": 10.0,
        "new_depth_record": 0.5,
        "at_optimal_y": 0.1,
        
        # Ore visibility - REDUCED passive rewards, added approach bonus
        "diamond_ore_visible": 5.0,   # Was 20 - reduced to encourage action
        "approaching_diamond": 15.0,  # NEW: bonus for moving toward diamond
        "other_ore_visible": 0.5,     # Was 1.0
        
        # Exploration
        "new_block_visited": 0.02,
        "horizontal_exploration": 0.05,
        
        # Efficiency
        "step_penalty": -0.001,
        "stuck_penalty": -0.2,
        "surface_penalty": -0.02,
        
        # Survival
        "damage_taken": -2.0,
        "low_health": -1.0,
        "danger_proximity": -0.5,
        "avoided_danger": 0.5,
    }
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset for new episode."""
        self.visited_positions: Set[Tuple[int, int, int]] = set()
        self.lowest_y = 320
        self.entered_diamond_zone = False
        self.seen_ores: Set[str] = set()
        self.mined_ores: Set[str] = set()
        self.prev_health = 20
        self.prev_position = None
        self.prev_danger_nearby = False
        self.stuck_counter = 0
        self.total_reward = 0
        self.step_count = 0
        self.horizontal_blocks_at_diamond = 0
        self.prev_closest_diamond_dist = float('inf')  # Track diamond approach
    
    def calculate(
        self, 
        observation: Dict[str, Any],
        prev_observation: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate reward for current step."""
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
        mined_ores_count = observation.get("minedOresCount", 0)
        danger_nearby = observation.get("dangerNearby", False)
        
        # === Terminal: Diamond in inventory ===
        if inventory.get("diamond", 0) > 0:
            reward += self.REWARDS["diamond_found"]
            breakdown["diamond_found"] = self.REWARDS["diamond_found"]
            return reward, breakdown
        
        # === Terminal: Death ===
        if health <= 0:
            reward += self.REWARDS["death"]
            breakdown["death"] = self.REWARDS["death"]
            return reward, breakdown
        
        # === Step penalty ===
        reward += self.REWARDS["step_penalty"]
        breakdown["step"] = self.REWARDS["step_penalty"]
        
        # === Mining rewards ===
        current_mined = len(self.mined_ores)
        if mined_ores_count > current_mined:
            # Check what was mined
            for block in nearby_blocks:
                ore_key = f"{block.get('name')}_{block.get('position', {})}"
                if ore_key not in self.mined_ores and "_ore" in block.get("name", ""):
                    self.mined_ores.add(ore_key)
                    name = block.get("name", "")
                    if "diamond" in name:
                        reward += self.REWARDS["mined_diamond_ore"]
                        breakdown["mined_diamond"] = self.REWARDS["mined_diamond_ore"]
                    elif "iron" in name:
                        reward += self.REWARDS["mined_iron_ore"]
                        breakdown["mined_iron"] = self.REWARDS["mined_iron_ore"]
                    elif "gold" in name:
                        reward += self.REWARDS["mined_gold_ore"]
                        breakdown["mined_gold"] = self.REWARDS["mined_gold_ore"]
                    elif "redstone" in name:
                        reward += self.REWARDS["mined_redstone_ore"]
                        breakdown["mined_redstone"] = self.REWARDS["mined_redstone_ore"]
                    else:
                        reward += self.REWARDS["mined_other_ore"]
                        breakdown["mined_other"] = self.REWARDS["mined_other_ore"]
        
        # === Y-Level rewards ===
        # Strong bonus for entering diamond zone (Y <= 16)
        if current_y <= 16 and not self.entered_diamond_zone:
            reward += self.REWARDS["enter_diamond_zone"]
            breakdown["enter_diamond_zone"] = self.REWARDS["enter_diamond_zone"]
            self.entered_diamond_zone = True
        
        # Progressive depth bonus - encourages going deeper
        if current_y < self.lowest_y:
            depth_gain = self.lowest_y - current_y
            # Stronger bonus when approaching optimal Y (-59)
            if current_y < 0:
                depth_bonus = self.REWARDS["new_depth_record"] * depth_gain * 2.0
            else:
                depth_bonus = self.REWARDS["new_depth_record"] * depth_gain
            reward += min(depth_bonus, 10.0)  # Cap at 10 per step
            breakdown["new_depth"] = depth_bonus
            self.lowest_y = current_y
        
        # Bonus for being at optimal diamond Y (-59 to -50)
        if -59 <= current_y <= -50:
            reward += self.REWARDS["at_optimal_y"] * 2.0
            breakdown["optimal_y"] = self.REWARDS["at_optimal_y"] * 2.0
        
        # Optimal Y-level bonus (diamond level)
        if -64 <= current_y <= -50:
            reward += self.REWARDS["at_optimal_y"]
            breakdown["optimal_y"] = self.REWARDS["at_optimal_y"]
            
            # Bonus for horizontal exploration at diamond level
            block_pos = (int(pos["x"]), int(pos["z"]))  # Ignore Y
            if block_pos not in [(p[0], p[2]) for p in self.visited_positions if -64 <= p[1] <= -50]:
                reward += self.REWARDS["horizontal_exploration"]
                breakdown["horizontal_explore"] = self.REWARDS["horizontal_exploration"]
                self.horizontal_blocks_at_diamond += 1
        
        # Surface penalty
        if current_y > 62:
            reward += self.REWARDS["surface_penalty"]
            breakdown["surface_penalty"] = self.REWARDS["surface_penalty"]
        
        # === Ore visibility ===
        closest_diamond_dist = float('inf')
        for block in nearby_blocks:
            name = block.get("name", "")
            ore_key = f"{name}_{block.get('position', {})}"
            
            # Track closest diamond distance
            if "diamond" in name and "_ore" in name:
                block_pos = block.get("position", {})
                dist = np.sqrt(
                    (block_pos.get("x", 0) - pos["x"])**2 +
                    (block_pos.get("y", 0) - pos["y"])**2 +
                    (block_pos.get("z", 0) - pos["z"])**2
                )
                closest_diamond_dist = min(closest_diamond_dist, dist)
            
            if "_ore" in name and ore_key not in self.seen_ores:
                self.seen_ores.add(ore_key)
                if "diamond" in name:
                    reward += self.REWARDS["diamond_ore_visible"]
                    breakdown["see_diamond"] = breakdown.get("see_diamond", 0) + self.REWARDS["diamond_ore_visible"]
                else:
                    reward += self.REWARDS["other_ore_visible"]
                    breakdown["see_ore"] = breakdown.get("see_ore", 0) + self.REWARDS["other_ore_visible"]
        
        # === Approaching diamond bonus ===
        if closest_diamond_dist < float('inf') and closest_diamond_dist < self.prev_closest_diamond_dist:
            approach_bonus = self.REWARDS["approaching_diamond"] * (self.prev_closest_diamond_dist - closest_diamond_dist)
            reward += min(approach_bonus, 30.0)  # Cap at 30
            breakdown["approaching_diamond"] = approach_bonus
        self.prev_closest_diamond_dist = closest_diamond_dist
        
        # === Exploration ===
        block_pos = (int(pos["x"]), int(pos["y"]), int(pos["z"]))
        if block_pos not in self.visited_positions:
            base_exploration = self.REWARDS["new_block_visited"]
            
            # 10X EXPLORATION BONUS at optimal diamond depth!
            if -59 <= current_y <= -45:
                exploration_reward = base_exploration * 10.0
                self.horizontal_blocks_at_diamond += 1
                breakdown["diamond_exploration"] = exploration_reward
            else:
                exploration_reward = base_exploration
                breakdown["exploration"] = exploration_reward
            
            reward += exploration_reward
            self.visited_positions.add(block_pos)
        
        # === MASSIVE bonus for first time exploring at optimal depth ===
        if -59 <= current_y <= -50 and self.horizontal_blocks_at_diamond == 0:
            reward += 50.0  # Big bonus for reaching and starting to mine here
            breakdown["first_diamond_level"] = 50.0
        
        # === Stuck detection ===
        if self.prev_position is not None:
            dist = np.sqrt(
                (pos["x"] - self.prev_position["x"])**2 +
                (pos["y"] - self.prev_position["y"])**2 +
                (pos["z"] - self.prev_position["z"])**2
            )
            if dist < 0.1:
                self.stuck_counter += 1
                if self.stuck_counter > 15:
                    reward += self.REWARDS["stuck_penalty"]
                    breakdown["stuck"] = self.REWARDS["stuck_penalty"]
            else:
                self.stuck_counter = 0
        self.prev_position = pos
        
        # === Survival rewards ===
        
        # Damage taken
        if health < self.prev_health:
            damage = self.prev_health - health
            damage_penalty = self.REWARDS["damage_taken"] * damage
            reward += damage_penalty
            breakdown["damage"] = damage_penalty
        self.prev_health = health
        
        # Low health
        if health < 5:
            reward += self.REWARDS["low_health"]
            breakdown["low_health"] = self.REWARDS["low_health"]
        
        # Danger proximity
        if danger_nearby:
            reward += self.REWARDS["danger_proximity"]
            breakdown["danger"] = self.REWARDS["danger_proximity"]
        
        # Avoided danger (was near danger, now not)
        if self.prev_danger_nearby and not danger_nearby:
            reward += self.REWARDS["avoided_danger"]
            breakdown["avoided_danger"] = self.REWARDS["avoided_danger"]
        self.prev_danger_nearby = danger_nearby
        
        self.total_reward += reward
        return reward, breakdown
    
    def get_stats(self) -> Dict[str, Any]:
        """Get episode statistics."""
        return {
            "total_reward": self.total_reward,
            "steps": self.step_count,
            "lowest_y": self.lowest_y,
            "blocks_visited": len(self.visited_positions),
            "ores_seen": len(self.seen_ores),
            "ores_mined": len(self.mined_ores),
            "entered_diamond_zone": self.entered_diamond_zone,
            "horizontal_at_diamond": self.horizontal_blocks_at_diamond,
        }