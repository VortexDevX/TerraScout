#!/usr/bin/env python3
"""
Test script for Terra Scout Gymnasium environment
"""

import sys
sys.path.insert(0, '.')

import gymnasium as gym
from agent.src.bridge.environment import TerraScoutEnv


def main():
    print("=" * 50)
    print("Terra Scout Gymnasium Environment Test")
    print("=" * 50)
    print()
    
    # Create environment
    print("[1] Creating environment...")
    env = TerraScoutEnv(host="localhost", port=3000, max_steps=100)
    print(f"    ✓ Action space: {env.action_space}")
    print(f"    ✓ Observation space keys: {list(env.observation_space.spaces.keys())}") # type: ignore
    
    # Reset
    print("\n[2] Resetting environment...")
    obs, info = env.reset()
    print(f"    ✓ Observation received")
    print(f"    ✓ Position: {obs['position']}")
    print(f"    ✓ Health: {obs['health'][0]}")
    
    # Take random actions
    print("\n[3] Taking 20 random actions...")
    total_reward = 0
    
    for i in range(20):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        if (i + 1) % 5 == 0:
            print(f"    Step {i+1}: action={action}, reward={reward:.4f}, pos_y={obs['position'][1]:.1f}")
        
        if terminated:
            print(f"    Episode terminated at step {i+1}")
            break
    
    print(f"\n    ✓ Total reward: {total_reward:.4f}")
    
    # Test specific actions
    print("\n[4] Testing specific actions...")
    
    action_names = [
        "noop", "forward", "back", "left", "right",
        "jump", "forward_jump", "dig", "look_up",
        "look_down", "look_left", "look_right"
    ]
    
    obs, info = env.reset()
    for action_idx in [1, 5, 6, 8, 11]:  # forward, jump, forward_jump, look_up, look_right
        obs, reward, terminated, truncated, info = env.step(action_idx)
        print(f"    ✓ {action_names[action_idx]}: pos=({obs['position'][0]:.1f}, {obs['position'][1]:.1f}, {obs['position'][2]:.1f})")
    
    # Close
    print("\n[5] Closing environment...")
    env.close()
    print("    ✓ Environment closed")
    
    print()
    print("=" * 50)
    print("✅ Gymnasium environment test passed!")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())