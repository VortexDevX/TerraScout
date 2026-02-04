#!/usr/bin/env python3
"""
Terra Scout Metrics Tracker
Track and visualize training performance
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


class MetricsTracker:
    """Track training metrics over time."""
    
    def __init__(self, save_dir: str = "training/logs/metrics"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.episode_data: List[Dict[str, Any]] = []
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log_episode(
        self,
        episode: int,
        reward: float,
        length: int,
        lowest_y: float,
        diamond_zone: bool,
        diamonds_found: int,
        ores_mined: int,
        strategy: str = "unknown",
        in_cave: bool = False,
    ):
        """Log a single episode."""
        # Ensure all numeric values are native Python types (not numpy)
        self.episode_data.append({
            "episode": int(episode),
            "reward": float(reward),
            "length": int(length),
            "lowest_y": float(lowest_y),
            "diamond_zone": bool(diamond_zone),
            "diamonds_found": int(diamonds_found),
            "ores_mined": int(ores_mined),
            "strategy": str(strategy),
            "in_cave": bool(in_cave),
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_summary(self, last_n: int = 100) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.episode_data:
            return {}
        
        recent = self.episode_data[-last_n:]
        
        # Convert numpy types to native Python types for JSON serialization
        return {
            "total_episodes": len(self.episode_data),
            "avg_reward": float(np.mean([e["reward"] for e in recent])),
            "avg_length": float(np.mean([e["length"] for e in recent])),
            "avg_lowest_y": float(np.mean([float(e["lowest_y"]) for e in recent])),
            "diamond_zone_rate": float(sum(1 for e in recent if e["diamond_zone"]) / len(recent)),
            "diamond_found_rate": float(sum(1 for e in recent if e["diamonds_found"] > 0) / len(recent)),
            "total_diamonds": int(sum(e["diamonds_found"] for e in self.episode_data)),
            "total_ores": int(sum(e["ores_mined"] for e in self.episode_data)),
            "best_reward": float(max(e["reward"] for e in self.episode_data)),
            "deepest_y": float(min(float(e["lowest_y"]) for e in self.episode_data)),
        }
    
    def print_summary(self, last_n: int = 100):
        """Print summary to console."""
        summary = self.get_summary(last_n)
        
        print("\n" + "=" * 50)
        print("TRAINING METRICS SUMMARY")
        print("=" * 50)
        print(f"Total Episodes: {summary.get('total_episodes', 0)}")
        print(f"Average Reward (last {last_n}): {summary.get('avg_reward', 0):.2f}")
        print(f"Diamond Zone Rate: {summary.get('diamond_zone_rate', 0)*100:.1f}%")
        print(f"Diamond Found Rate: {summary.get('diamond_found_rate', 0)*100:.1f}%")
        print(f"Total Diamonds: {summary.get('total_diamonds', 0)}")
        print(f"Deepest Y Level: {summary.get('deepest_y', 64)}")
        print(f"Best Reward: {summary.get('best_reward', 0):.2f}")
        print("=" * 50 + "\n")
    
    def save(self):
        """Save metrics to file."""
        filepath = self.save_dir / f"metrics_{self.run_id}.json"
        with open(filepath, "w") as f:
            json.dump({
                "run_id": self.run_id,
                "summary": self.get_summary(),
                "episodes": self.episode_data,
            }, f, indent=2)
        print(f"Metrics saved to {filepath}")
    
    def load(self, filepath: str):
        """Load metrics from file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        self.episode_data = data.get("episodes", [])
        self.run_id = data.get("run_id", self.run_id)


if __name__ == "__main__":
    # Test metrics tracker
    tracker = MetricsTracker()
    
    for i in range(10):
        tracker.log_episode(
            episode=i,
            reward=np.random.uniform(100, 500),
            length=300,
            lowest_y=np.random.uniform(-63, -50),
            diamond_zone=True,
            diamonds_found=1 if np.random.random() > 0.8 else 0,
            ores_mined=np.random.randint(5, 20),
            strategy="strip_mine",
            in_cave=np.random.random() > 0.5,
        )
    
    tracker.print_summary()
    tracker.save()