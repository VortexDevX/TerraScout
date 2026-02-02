#!/usr/bin/env python3
"""
Terra Scout Installation Verification Script (Mineflayer Edition)
"""

import sys
import os
import subprocess
import shutil
from typing import Tuple

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {text}")
    print('=' * 50)


def print_status(name: str, success: bool, details: str = "") -> None:
    icon = f"{GREEN}[✓]{RESET}" if success else f"{RED}[✗]{RESET}"
    detail_str = f" ({details})" if details else ""
    print(f"{icon} {name}{detail_str}")


def check_python_version() -> Tuple[bool, str]:
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    success = version.major == 3 and version.minor >= 11
    return success, version_str


def check_java() -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True
        )
        output = result.stderr
        if "21" in output or "17" in output:
            lines = output.split('\n')
            return True, lines[0] if lines else "Found"
        return False, "Wrong version"
    except FileNotFoundError:
        return False, "Not found"


def check_node() -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        major = int(version.lstrip('v').split('.')[0])
        return major >= 18, version
    except Exception:
        return False, "Not found"


def check_npm() -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        return True, result.stdout.strip()
    except Exception:
        return False, "Not found"


def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]: # type: ignore
    import_name = import_name or package_name
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "installed")
        return True, version
    except ImportError:
        return False, "Not installed"


def check_cuda() -> Tuple[bool, str]:
    try:
        import torch
        if torch.cuda.is_available():
            return True, f"{torch.cuda.get_device_name(0)} (CUDA {torch.version.cuda})" # type: ignore
        return False, "Not available"
    except ImportError:
        return False, "PyTorch not installed"


def check_mineflayer_installed() -> Tuple[bool, str]:
    bot_path = os.path.join(os.path.dirname(__file__), "..", "bot")
    node_modules = os.path.join(bot_path, "node_modules", "mineflayer")
    if os.path.exists(node_modules):
        try:
            pkg_json = os.path.join(node_modules, "package.json")
            import json
            with open(pkg_json) as f:
                pkg = json.load(f)
                return True, pkg.get("version", "installed")
        except Exception:
            return True, "installed"
    return False, "Not installed"


def main() -> int:
    print_header("Terra Scout Installation Verification")
    print(f"{CYAN}Mineflayer + Python Bridge Edition{RESET}\n")

    all_passed = True
    critical_failed = False

    # Python
    success, details = check_python_version()
    print_status("Python 3.11+", success, details)
    if not success:
        critical_failed = True
    all_passed &= success

    # Java
    success, details = check_java()
    print_status("Java 17/21", success, details)
    all_passed &= success

    # Node.js
    success, details = check_node()
    print_status("Node.js 18+", success, details)
    if not success:
        critical_failed = True
    all_passed &= success

    # npm
    success, details = check_npm()
    print_status("npm", success, details)
    all_passed &= success

    print()

    # PyTorch
    success, details = check_package("torch")
    print_status("PyTorch", success, details)
    if not success:
        critical_failed = True
    all_passed &= success

    # CUDA
    success, details = check_cuda()
    print_status("CUDA", success, details)

    # Gymnasium
    success, details = check_package("gymnasium")
    print_status("Gymnasium", success, details)
    all_passed &= success

    # Stable-Baselines3
    success, details = check_package("stable_baselines3")
    print_status("Stable-Baselines3", success, details)
    all_passed &= success

    # httpx
    success, details = check_package("httpx")
    print_status("httpx", success, details)
    all_passed &= success

    # websockets
    success, details = check_package("websockets")
    print_status("websockets", success, details)
    all_passed &= success

    print()

    # Mineflayer
    success, details = check_mineflayer_installed()
    print_status("Mineflayer (Node.js)", success, details)
    if not success:
        print(f"  {YELLOW}Run: cd bot && npm install{RESET}")
    all_passed &= success

    # Summary
    print_header("Summary")

    if all_passed:
        print(f"{GREEN}✅ ALL CHECKS PASSED{RESET}")
        print("Terra Scout is ready for development!")
        print()
        print("Next steps:")
        print("  1. Download Minecraft server (see server/README.md)")
        print("  2. Start Minecraft server: cd server && ./start.ps1")
        print("  3. Start bot: cd bot && npm start")
        print("  4. Run Python agent")
        return 0
    elif critical_failed:
        print(f"{RED}❌ CRITICAL CHECKS FAILED{RESET}")
        return 1
    else:
        print(f"{YELLOW}⚠️ SOME CHECKS FAILED{RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(main())