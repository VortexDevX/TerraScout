#!/usr/bin/env python3
"""
Terra Scout Training Script
Full training pipeline with PPO
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    BaseCallback,
    CheckpointCallback,
    EvalCallback,
)
from stable_baselines3.common.logger import configure
from stable_baselines3.common.monitor import Monitor

from agent.src.bridge.environment import TerraScoutEnv


class TerraScoutCallback(BaseCallback):
    """Custom callback for Terra Scout training."""
    
    def __init__(self, verbose=0, log_freq=100):
        super().__init__(verbose)
        self.log_freq = log_freq
        self.episode_rewards = []
        self.episode_lengths = []
        self.episode_stats = []
        self.current_episode_reward = 0
        self.current_episode_length = 0
        
    def _on_step(self) -> bool:
        self.current_episode_reward += self.locals.get('rewards', [0])[0]
        self.current_episode_length += 1
        
        # Check for episode end
        dones = self.locals.get('dones', [False])
        infos = self.locals.get('infos', [{}])
        
        if dones[0]:
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)
            
            # Get episode stats
            if 'episode_stats' in infos[0]:
                self.episode_stats.append(infos[0]['episode_stats'])
            
            # Log episode
            ep_num = len(self.episode_rewards)
            if ep_num % self.log_freq == 0 or ep_num <= 10:
                avg_reward = np.mean(self.episode_rewards[-100:])
                avg_length = np.mean(self.episode_lengths[-100:])
                
                stats = self.episode_stats[-1] if self.episode_stats else {}
                lowest_y = stats.get('lowest_y', 'N/A')
                diamond_zone = stats.get('entered_diamond_zone', False)
                
                print(f"  Episode {ep_num}: "
                      f"reward={self.current_episode_reward:.2f}, "
                      f"avg={avg_reward:.2f}, "
                      f"len={self.current_episode_length}, "
                      f"lowest_y={lowest_y}, "
                      f"diamond_zone={diamond_zone}")
            
            # Reset
            self.current_episode_reward = 0
            self.current_episode_length = 0
        
        return True
    
    def _on_training_end(self) -> None:
        if self.episode_rewards:
            print(f"\nTraining Summary:")
            print(f"  Total episodes: {len(self.episode_rewards)}")
            print(f"  Average reward: {np.mean(self.episode_rewards):.2f}")
            print(f"  Best reward: {np.max(self.episode_rewards):.2f}")
            
            if self.episode_stats:
                diamond_entries = sum(1 for s in self.episode_stats if s.get('entered_diamond_zone'))
                print(f"  Diamond zone entries: {diamond_entries}/{len(self.episode_stats)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Train Terra Scout Agent")
    
    # Environment
    parser.add_argument("--host", type=str, default="localhost", help="Bot API host")
    parser.add_argument("--port", type=int, default=3000, help="Bot API port")
    parser.add_argument("--max-steps", type=int, default=2000, help="Max steps per episode")
    
    # Training
    parser.add_argument("--total-timesteps", type=int, default=100000, help="Total training timesteps")
    parser.add_argument("--learning-rate", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--n-steps", type=int, default=2048, help="Steps per update")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--n-epochs", type=int, default=10, help="Epochs per update")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
    parser.add_argument("--gae-lambda", type=float, default=0.95, help="GAE lambda")
    parser.add_argument("--clip-range", type=float, default=0.2, help="PPO clip range")
    parser.add_argument("--ent-coef", type=float, default=0.01, help="Entropy coefficient")
    
    # Saving
    parser.add_argument("--save-freq", type=int, default=10000, help="Checkpoint save frequency")
    parser.add_argument("--save-path", type=str, default="training/checkpoints", help="Checkpoint directory")
    parser.add_argument("--log-path", type=str, default="training/logs", help="Log directory")
    
    # Resume
    parser.add_argument("--resume", type=str, default=None, help="Resume from checkpoint")
    
    # Misc
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--device", type=str, default="auto", help="Device (auto/cuda/cpu)")
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 60)
    print("Terra Scout Training")
    print("=" * 60)
    print()
    
    # Create directories
    os.makedirs(args.save_path, exist_ok=True)
    os.makedirs(args.log_path, exist_ok=True)
    
    # Create experiment name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_name = f"terra_scout_{timestamp}"
    
    print(f"Experiment: {exp_name}")
    print(f"Device: {args.device}")
    print(f"Total timesteps: {args.total_timesteps}")
    print()
    
    # Create environment
    print("[1] Creating environment...")
    env = TerraScoutEnv(
        host=args.host,
        port=args.port,
        max_steps=args.max_steps,
        use_enhanced_obs=True,
        use_enhanced_rewards=True,
    )
    env = Monitor(env)
    print(f"    Action space: {env.action_space}")
    print(f"    Observation space: {env.observation_space}")
    print()
    
    # Create or load model
    if args.resume:
        print(f"[2] Loading model from {args.resume}...")
        model = PPO.load(args.resume, env=env, device=args.device)
    else:
        print("[2] Creating new PPO model...")
        model = PPO(
            "MlpPolicy",
            env,
            learning_rate=args.learning_rate,
            n_steps=args.n_steps,
            batch_size=args.batch_size,
            n_epochs=args.n_epochs,
            gamma=args.gamma,
            gae_lambda=args.gae_lambda,
            clip_range=args.clip_range,
            ent_coef=args.ent_coef,
            verbose=0,
            device=args.device,
            seed=args.seed,
            tensorboard_log=args.log_path,
        )
    
    print(f"    Model device: {model.device}")
    print()
    
    # Setup callbacks
    callbacks = [
        TerraScoutCallback(verbose=1, log_freq=10),
        CheckpointCallback(
            save_freq=args.save_freq,
            save_path=args.save_path,
            name_prefix=exp_name,
        ),
    ]
    
    # Train
    print("[3] Starting training...")
    print()
    
    try:
        model.learn(
            total_timesteps=args.total_timesteps,
            callback=callbacks,
            progress_bar=True,
            tb_log_name=exp_name,
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
    
    # Save final model
    final_path = os.path.join(args.save_path, f"{exp_name}_final")
    model.save(final_path)
    print(f"\n[4] Final model saved to {final_path}.zip")
    
    # Cleanup
    env.close()
    print("\nTraining complete!")


if __name__ == "__main__":
    main()