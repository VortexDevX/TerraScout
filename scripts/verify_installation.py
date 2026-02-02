#!/usr/bin/env python3
"""
Terra Scout Installation Verification Script

Verifies that all dependencies are correctly installed
and the environment is ready for development.
"""

import sys
import os
import subprocess
from typing import Tuple, List

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 50}")
    print(f"  {text}")
    print('=' * 50)


def print_status(name: str, success: bool, details: str = "") -> None:
    """Print a status line."""
    icon = f"{GREEN}[✓]{RESET}" if success else f"{RED}[✗]{RESET}"
    detail_str = f" ({details})" if details else ""
    print(f"{icon} {name}{detail_str}")


def check_python_version() -> Tuple[bool, str]:
    """Check Python version is 3.10.x."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    success = version.major == 3 and version.minor == 10
    return success, version_str


def check_java_home() -> Tuple[bool, str]:
    """Check if JAVA_HOME is set."""
    java_home = os.environ.get("JAVA_HOME", "")
    success = bool(java_home) and os.path.exists(java_home)
    return success, java_home if success else "Not set"


def check_java_version() -> Tuple[bool, str]:
    """Check Java version is 1.8.x."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True
        )
        output = result.stderr  # Java outputs version to stderr
        
        if "1.8" in output or "1.8.0" in output:
            return True, "1.8.x"
        else:
            # Extract version from output
            lines = output.split('\n')
            version = lines[0] if lines else "Unknown"
            return False, version
    except FileNotFoundError:
        return False, "Java not found"


def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Check if a Python package is installed."""
    import_name = import_name or package_name
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "installed")
        return True, version
    except ImportError:
        return False, "Not installed"


def check_cuda() -> Tuple[bool, str]:
    """Check if CUDA is available."""
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            cuda_version = torch.version.cuda
            return True, f"{device_name} (CUDA {cuda_version})"
        else:
            return False, "CUDA not available"
    except ImportError:
        return False, "PyTorch not installed"


def test_minerl_environment() -> Tuple[bool, str]:
    """Test MineRL environment creation."""
    try:
        import gymnasium as gym
        import minerl
        
        print("\n  Creating MineRL environment (this may take a moment)...")
        env = gym.make("MineRLNavigateDense-v0")
        
        print("  Resetting environment...")
        obs, info = env.reset()
        
        print("  Taking test step...")
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        print("  Closing environment...")
        env.close()
        
        return True, "All operations successful"
    except Exception as e:
        return False, str(e)[:50]


def main() -> int:
    """Run all verification checks."""
    
    print_header("Terra Scout Installation Verification")
    
    all_passed = True
    critical_failed = False
    
    # Python version
    success, details = check_python_version()
    print_status("Python 3.10.x", success, details)
    if not success:
        critical_failed = True
    all_passed &= success
    
    # Java
    success, details = check_java_home()
    print_status("JAVA_HOME is set", success, details)
    all_passed &= success
    
    success, details = check_java_version()
    print_status("Java version 1.8.x", success, details)
    if not success:
        critical_failed = True
    all_passed &= success
    
    # PyTorch
    success, details = check_package("torch")
    print_status("PyTorch", success, details)
    if not success:
        critical_failed = True
    all_passed &= success
    
    # CUDA
    success, details = check_cuda()
    print_status("CUDA available", success, details)
    # CUDA is not critical for basic operation
    
    # MineRL
    success, details = check_package("minerl")
    print_status("MineRL installed", success, details)
    if not success:
        critical_failed = True
    all_passed &= success
    
    # Stable-Baselines3
    success, details = check_package("stable_baselines3", "stable_baselines3")
    print_status("Stable-Baselines3", success, details)
    if not success:
        critical_failed = True
    all_passed &= success
    
    # Gymnasium
    success, details = check_package("gymnasium")
    print_status("Gymnasium", success, details)
    if not success:
        critical_failed = True
    all_passed &= success
    
    # Additional packages
    packages = [
        ("numpy", "numpy"),
        ("opencv-python", "cv2"),
        ("PyYAML", "yaml"),
        ("tqdm", "tqdm"),
        ("tensorboard", "tensorboard"),
        ("matplotlib", "matplotlib"),
    ]
    
    print("\n  Additional packages:")
    for package_name, import_name in packages:
        success, details = check_package(package_name, import_name)
        print_status(f"  {package_name}", success, details)
    
    # Environment test (only if critical packages installed)
    if not critical_failed:
        print_header("Environment Test")
        success, details = test_minerl_environment()
        print_status("MineRL environment test", success, details)
        all_passed &= success
    else:
        print(f"\n{YELLOW}Skipping environment test due to missing critical packages.{RESET}")
    
    # Final summary
    print_header("Summary")
    
    if all_passed:
        print(f"{GREEN}✅ ALL CHECKS PASSED{RESET}")
        print("Terra Scout is ready for development!")
        return 0
    elif critical_failed:
        print(f"{RED}❌ CRITICAL CHECKS FAILED{RESET}")
        print("Please fix the issues above before continuing.")
        print("See docs/guides/TROUBLESHOOTING.md for help.")
        return 1
    else:
        print(f"{YELLOW}⚠️ SOME CHECKS FAILED{RESET}")
        print("Non-critical issues detected. Development may proceed with limitations.")
        return 0


if __name__ == "__main__":
    sys.exit(main())