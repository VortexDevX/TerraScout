"""
Pytest configuration and shared fixtures for agent tests.
"""

import pytest
import numpy as np
import torch


@pytest.fixture(scope="session")
def device():
    """Get the compute device for tests."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def sample_observation():
    """Create a sample observation for testing."""
    return {
        "pov": np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8),
        "inventory": {
            "coal": 0,
            "cobblestone": 0,
            "diamond": 0,
            "dirt": 0,
            "iron_ore": 0,
        },
        "equipped_items": {
            "mainhand": {
                "damage": 0,
                "maxDamage": 0,
                "type": "none"
            }
        },
        "life_stats": {
            "life": 20.0,
            "food": 20.0,
            "air": 300.0
        }
    }


@pytest.fixture
def sample_action():
    """Create a sample action for testing."""
    return {
        "forward": 1,
        "back": 0,
        "left": 0,
        "right": 0,
        "jump": 0,
        "sneak": 0,
        "sprint": 0,
        "attack": 1,
        "camera": (0.0, 0.0)
    }


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return {
        "agent": {
            "name": "TerraScout-Test",
            "version": "0.1.0"
        },
        "model": {
            "feature_extractor": {
                "channels": [32, 64],
                "kernel_sizes": [8, 4],
                "strides": [4, 2]
            },
            "policy_net": {
                "hidden_sizes": [128]
            },
            "value_net": {
                "hidden_sizes": [128]
            }
        },
        "algorithm": {
            "learning_rate": 0.0003,
            "batch_size": 32,
            "gamma": 0.99
        }
    }


@pytest.fixture
def batch_observations(sample_observation):
    """Create a batch of observations for testing."""
    batch_size = 4
    return {
        "pov": np.stack([sample_observation["pov"]] * batch_size),
        "inventory": sample_observation["inventory"],
        "life_stats": sample_observation["life_stats"]
    }


class MockEnv:
    """Mock environment for testing without MineRL dependency."""
    
    def __init__(self):
        self.observation_space = None
        self.action_space = None
        self._step_count = 0
        self._max_steps = 100
    
    def reset(self, seed=None):
        self._step_count = 0
        obs = {
            "pov": np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8),
            "inventory": {"diamond": 0},
            "life_stats": {"life": 20.0}
        }
        return obs, {}
    
    def step(self, action):
        self._step_count += 1
        obs = {
            "pov": np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8),
            "inventory": {"diamond": 0},
            "life_stats": {"life": 20.0}
        }
        reward = -0.001
        terminated = self._step_count >= self._max_steps
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info
    
    def close(self):
        pass


@pytest.fixture
def mock_env():
    """Create a mock environment for testing."""
    return MockEnv()