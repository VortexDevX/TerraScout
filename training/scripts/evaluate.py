#!/usr/bin/env python3
"""
Terra Scout Evaluation Script
Evaluate trained agent performance
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
from stable_baselines3 import PPO

from agent.src.bridge.environment import TerraScoutEnv


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate Terra Scout Agent")
    parser.add_argument("--model", type=str, required=True, help="Model path")
    parser.add_argument("--episodes", type=int, default=10, help="Number of episodes")
    parser.add_argument("--max-steps", type=int, default=2000, help="Max steps per episode")
    parser.add_argument("--host", type=str, default="localhost", help="Bot API host")
    parser.add_argument("--port", type=int, default=3000, help="Bot API port")
    parser.add_argument("--deterministic", action="store_true", help="Use deterministic actions")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 60)
    print("Terra Scout Evaluation")
    print("=" * 60)
    print()
    
    # Load model
    print(f"Loading model: {args.model}")
    model = PPO.load(args.model)
    
    # Create environment
    print("Creating environment...")
    env = TerraScoutEnv(
        host=args.host,
        port=args.port,
        max_steps=args.max_steps,
        use_enhanced_obs=True,
        use_enhanced_rewards=True,
    )
    
    # Evaluation metrics
    episode_rewards = []
    episode_lengths = []
    lowest_y_levels = []
    diamond_zone_entries = []
    diamonds_found = 0
    
    print(f"\nEvaluating for {args.episodes} episodes...")
    print()
    
    for ep in range(args.episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        done = False
        
        while not done and steps < args.max_steps:
            action, _ = model.predict(obs, deterministic=args.deterministic)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            done = terminated or truncated
            
            if args.verbose and steps % 100 == 0:
                stats = info.get('episode_stats', {})
                print(f"  Step {steps}: y={stats.get('lowest_y', 'N/A')}, reward={episode_reward:.2f}")
        
        # Get final stats
        stats = info.get('episode_stats', {})
        lowest_y = stats.get('lowest_y', 320)
        entered_diamond = stats.get('entered_diamond_zone', False)
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(steps)
        lowest_y_levels.append(lowest_y)
        diamond_zone_entries.append(entered_diamond)
        
        # Check for diamond
        raw_obs = info.get('raw_observation', {})
        if raw_obs and raw_obs.get('inventory', {}).get('diamond', 0) > 0:
            diamonds_found += 1
        
        print(f"Episode {ep + 1}/{args.episodes}: "
              f"reward={episode_reward:.2f}, "
              f"steps={steps}, "
              f"lowest_y={lowest_y}, "
              f"diamond_zone={entered_diamond}")
    
    # Print summary
    print()
    print("=" * 60)
    print("Evaluation Summary")
    print("=" * 60)
    print(f"Episodes: {args.episodes}")
    print()
    print("Rewards:")
    print(f"  Mean: {np.mean(episode_rewards):.2f}")
    print(f"  Std: {np.std(episode_rewards):.2f}")
    print(f"  Min: {np.min(episode_rewards):.2f}")
    print(f"  Max: {np.max(episode_rewards):.2f}")
    print()
    print("Episode Length:")
    print(f"  Mean: {np.mean(episode_lengths):.0f}")
    print(f"  Max: {np.max(episode_lengths):.0f}")
    print()
    print("Exploration:")
    print(f"  Avg Lowest Y: {np.mean(lowest_y_levels):.1f}")
    print(f"  Best Lowest Y: {np.min(lowest_y_levels):.1f}")
    print(f"  Diamond Zone Rate: {sum(diamond_zone_entries)}/{args.episodes} ({100*sum(diamond_zone_entries)/args.episodes:.1f}%)")
    print(f"  Diamonds Found: {diamonds_found}/{args.episodes}")
    print()
    
    env.close()


if __name__ == "__main__":
    main()