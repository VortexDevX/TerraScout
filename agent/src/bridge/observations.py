"""
Terra Scout Observation Processing
Converts raw bot observations into RL-ready format
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class ObservationProcessor:
    """
    Processes raw observations from Mineflayer bot
    into structured format for RL agent.
    """
    
    # Valuable ore types for diamond finding
    VALUABLE_ORES = {
        "diamond_ore": 10.0,
        "deepslate_diamond_ore": 10.0,
        "iron_ore": 1.0,
        "deepslate_iron_ore": 1.0,
        "gold_ore": 2.0,
        "deepslate_gold_ore": 2.0,
        "redstone_ore": 3.0,
        "deepslate_redstone_ore": 3.0,
        "lapis_ore": 2.5,
        "deepslate_lapis_ore": 2.5,
        "coal_ore": 0.5,
        "deepslate_coal_ore": 0.5,
        "emerald_ore": 5.0,
        "deepslate_emerald_ore": 5.0,
    }
    
    # Dangerous blocks
    DANGEROUS_BLOCKS = {"lava", "fire", "cactus", "magma_block", "sweet_berry_bush"}
    
    # Diamond Y-level range (1.21+)
    DIAMOND_Y_MIN = -64
    DIAMOND_Y_MAX = 16
    DIAMOND_OPTIMAL_Y = -59
    
    def __init__(self):
        self.visited_positions = set()
        self.lowest_y = 320  # Track lowest Y reached
        self.ores_found = {}
        self.start_position = None
    
    def reset(self):
        """Reset tracking for new episode."""
        self.visited_positions.clear()
        self.lowest_y = 320
        self.ores_found.clear()
        self.start_position = None
    
    def process(self, raw_obs: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Process raw observation into structured format.
        
        Args:
            raw_obs: Raw observation from bot
            
        Returns:
            Processed observation dict with numpy arrays
        """
        if raw_obs is None:
            return self._empty_observation()
        
        # Extract position
        pos = raw_obs.get("position", {"x": 0, "y": 64, "z": 0})
        position = np.array([pos["x"], pos["y"], pos["z"]], dtype=np.float32)
        
        # Track start position
        if self.start_position is None:
            self.start_position = position.copy()
        
        # Track lowest Y
        if pos["y"] < self.lowest_y:
            self.lowest_y = pos["y"]
        
        # Track visited positions (discretized)
        block_pos = (int(pos["x"]), int(pos["y"]), int(pos["z"]))
        is_new_position = block_pos not in self.visited_positions
        self.visited_positions.add(block_pos)
        
        # Process nearby blocks
        nearby_blocks = raw_obs.get("nearbyBlocks", [])
        block_features = self._process_nearby_blocks(nearby_blocks, position)
        
        # Process inventory
        inventory = raw_obs.get("inventory", {})
        inventory_features = self._process_inventory(inventory)
        
        # Health and food
        health = raw_obs.get("health", 20)
        food = raw_obs.get("food", 20)
        
        # Orientation
        yaw = raw_obs.get("yaw", 0)
        pitch = raw_obs.get("pitch", 0)
        
        # Y-level features
        y_level_features = self._process_y_level(pos["y"])
        
        return {
            # Core state
            "position": position,
            "health": np.array([health / 20.0], dtype=np.float32),  # Normalized
            "food": np.array([food / 20.0], dtype=np.float32),  # Normalized
            "orientation": np.array([
                np.sin(yaw), np.cos(yaw),
                np.sin(pitch), np.cos(pitch)
            ], dtype=np.float32),
            
            # Y-level info (crucial for diamond finding)
            "y_level": y_level_features,
            
            # Block features
            "nearby_blocks": block_features,
            
            # Inventory
            "inventory": inventory_features,
            
            # Exploration state
            "exploration": np.array([
                len(self.visited_positions) / 1000.0,  # Normalized visited count
                float(is_new_position),  # Is this a new position
                (self.start_position[1] - pos["y"]) / 100.0 if self.start_position is not None else 0,  # Depth from start
            ], dtype=np.float32),
        }
    
    def _process_y_level(self, y: float) -> np.ndarray:
        """Process Y-level into features."""
        return np.array([
            y / 320.0,  # Normalized Y
            float(y <= self.DIAMOND_Y_MAX),  # In diamond zone
            float(y <= 0),  # Below sea level (deepslate zone)
            float(self.DIAMOND_Y_MIN <= y <= self.DIAMOND_Y_MAX),  # In optimal range
            max(0, (self.DIAMOND_Y_MAX - y) / 80.0),  # Progress into diamond zone
        ], dtype=np.float32)
    
    def _process_nearby_blocks(
        self, 
        blocks: List[Dict], 
        position: np.ndarray
    ) -> np.ndarray:
        """Process nearby blocks into feature vector."""
        features = np.zeros(10, dtype=np.float32)
        
        ore_count = 0
        diamond_ore_count = 0
        danger_count = 0
        stone_count = 0
        air_count = 0
        
        closest_ore_dist = 100.0
        closest_diamond_dist = 100.0
        
        for block in blocks:
            name = block.get("name", "")
            block_pos = block.get("position", {})
            
            # Calculate distance
            bx = block_pos.get("x", 0)
            by = block_pos.get("y", 0)
            bz = block_pos.get("z", 0)
            dist = np.sqrt(
                (bx - position[0])**2 + 
                (by - position[1])**2 + 
                (bz - position[2])**2
            )
            
            # Count block types
            if name in self.VALUABLE_ORES:
                ore_count += 1
                if dist < closest_ore_dist:
                    closest_ore_dist = dist
                    
                if "diamond" in name:
                    diamond_ore_count += 1
                    if dist < closest_diamond_dist:
                        closest_diamond_dist = dist
                    
                # Track found ores
                self.ores_found[name] = self.ores_found.get(name, 0) + 1
                    
            elif name in self.DANGEROUS_BLOCKS:
                danger_count += 1
                
            elif name in ("stone", "deepslate", "granite", "diorite", "andesite"):
                stone_count += 1
                
            elif name == "air" or name == "cave_air":
                air_count += 1
        
        features[0] = min(ore_count / 10.0, 1.0)  # Ore density
        features[1] = min(diamond_ore_count / 5.0, 1.0)  # Diamond ore density
        features[2] = min(danger_count / 5.0, 1.0)  # Danger density
        features[3] = min(stone_count / 50.0, 1.0)  # Stone density (mineable)
        features[4] = min(air_count / 50.0, 1.0)  # Air density (caves)
        features[5] = 1.0 - min(closest_ore_dist / 10.0, 1.0)  # Ore proximity
        features[6] = 1.0 - min(closest_diamond_dist / 10.0, 1.0)  # Diamond proximity
        features[7] = float(diamond_ore_count > 0)  # Diamond visible
        features[8] = float(ore_count > 0)  # Any ore visible
        features[9] = float(danger_count > 0)  # Danger nearby
        
        return features
    
    def _process_inventory(self, inventory: Dict[str, int]) -> np.ndarray:
        """Process inventory into feature vector."""
        features = np.zeros(8, dtype=np.float32)
        
        # Key items for diamond finding
        features[0] = min(inventory.get("diamond", 0) / 10.0, 1.0)
        features[1] = min(inventory.get("iron_ingot", 0) / 64.0, 1.0)
        features[2] = min(inventory.get("coal", 0) / 64.0, 1.0)
        features[3] = min(inventory.get("cobblestone", 0) / 64.0, 1.0)
        features[4] = min(inventory.get("torch", 0) / 64.0, 1.0)
        features[5] = float(inventory.get("diamond", 0) > 0)  # Has diamond
        features[6] = float(inventory.get("iron_pickaxe", 0) > 0 or 
                          inventory.get("diamond_pickaxe", 0) > 0)  # Has good pickaxe
        features[7] = min(sum(inventory.values()) / 100.0, 1.0)  # Total items
        
        return features
    
    def _empty_observation(self) -> Dict[str, np.ndarray]:
        """Return empty observation."""
        return {
            "position": np.zeros(3, dtype=np.float32),
            "health": np.array([1.0], dtype=np.float32),
            "food": np.array([1.0], dtype=np.float32),
            "orientation": np.zeros(4, dtype=np.float32),
            "y_level": np.zeros(5, dtype=np.float32),
            "nearby_blocks": np.zeros(10, dtype=np.float32),
            "inventory": np.zeros(8, dtype=np.float32),
            "exploration": np.zeros(3, dtype=np.float32),
        }
    
    def get_flat_observation(self, raw_obs: Dict[str, Any]) -> np.ndarray:
        """Get flattened observation vector."""
        obs = self.process(raw_obs)
        return np.concatenate([
            obs["position"],        # 3
            obs["health"],          # 1
            obs["food"],            # 1
            obs["orientation"],     # 4
            obs["y_level"],         # 5
            obs["nearby_blocks"],   # 10
            obs["inventory"],       # 8
            obs["exploration"],     # 3
        ])  # Total: 35