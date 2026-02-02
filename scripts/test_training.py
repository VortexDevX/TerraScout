#!/usr/bin/env python3
"""
Simple training test for Terra Scout
Uses Stable-Baselines3 PPO with custom environment
"""

import sys
sys.path.insert(0, '.')

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

from agent.src.bridge.environment import TerraScoutEnv


class SimpleCallback(BaseCallback):
    """Simple callback to print training progress."""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.current_rewards = 0
    
    def _on_step(self) -> bool:
        self.current_rewards += self.locals.get('rewards', [0])[0]
        
        # Check for episode end
        if self.locals.get('dones', [False])[0]:
            self.episode_rewards.append(self.current_rewards)
            if len(self.episode_rewards) % 1 == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                print(f"  Episode {len(self.episode_rewards)}: reward={self.current_rewards:.2f}, avg={avg_reward:.2f}")
            self.current_rewards = 0
        
        return True


def main():
    print("=" * 50)
    print("Terra Scout Training Test")
    print("=" * 50)
    print()
    
    # Create environment
    print("[1] Creating environment...")
    env = TerraScoutEnv(host="localhost", port=3000, max_steps=200)
    print("    ✓ Environment created")
    
    # Create model
    print("\n[2] Creating PPO model...")
    model = PPO(
        "MultiInputPolicy",
        env,
        verbose=0,
        learning_rate=3e-4,
        n_steps=64,
        batch_size=32,
        n_epochs=5,
        gamma=0.99,
        device="auto"
    )
    print("    ✓ Model created")
    print(f"    ✓ Device: {model.device}")
    
    # Train for a few steps
    print("\n[3] Training for 500 steps (this is just a test)...")
    print()
    
    callback = SimpleCallback()
    
    try:
        model.learn(
            total_timesteps=500,
            callback=callback,
            progress_bar=True
        )
        print()
        print("    ✓ Training completed")
    except KeyboardInterrupt:
        print("\n    ⚠ Training interrupted by user")
    except Exception as e:
        print(f"\n    ✗ Training error: {e}")
        env.close()
        return 1
    
    # Save model
    print("\n[4] Saving model...")
    model.save("training/checkpoints/test_model")
    print("    ✓ Model saved to training/checkpoints/test_model.zip")
    
    # Quick evaluation
    print("\n[5] Quick evaluation (3 episodes)...")
    
    total_rewards = []
    for ep in range(3):
        obs, info = env.reset()
        episode_reward = 0
        done = False
        steps = 0
        
        while not done and steps < 100:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action) # type: ignore
            episode_reward += reward
            done = terminated or truncated
            steps += 1
        
        total_rewards.append(episode_reward)
        print(f"    Episode {ep+1}: reward={episode_reward:.2f}, steps={steps}")
    
    print(f"\n    ✓ Average reward: {np.mean(total_rewards):.2f}")
    
    # Cleanup
    print("\n[6] Cleaning up...")
    env.close()
    print("    ✓ Done")
    
    print()
    print("=" * 50)
    print("✅ Training test completed!")
    print("=" * 50)
    print()
    print("Note: This was just a short test. For actual training,")
    print("you'll need many more timesteps (100k+) and proper")
    print("hyperparameter tuning.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())