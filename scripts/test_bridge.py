#!/usr/bin/env python3
"""
Test script for Terra Scout bridge connection
"""

import time
import sys
sys.path.insert(0, '.')

from agent.src.bridge import BridgeClient


def main():
    print("=" * 50)
    print("Terra Scout Bridge Test")
    print("=" * 50)
    print()
    
    # Create client
    client = BridgeClient(host="localhost", port=3000)
    
    # Test 1: Health check
    print("[1] Testing health check...")
    if client.health_check():
        print("    ✓ Bot server is running")
    else:
        print("    ✗ Bot server not responding!")
        print("    Make sure bot is running: cd bot && npm start")
        return 1
    
    # Test 2: Get status
    print("\n[2] Testing status endpoint...")
    status = client.get_status()
    if "error" not in status:
        print(f"    ✓ Connected: {status.get('connected')}")
        print(f"    ✓ Steps: {status.get('stepCount')}")
    else:
        print(f"    ✗ Error: {status['error']}")
        return 1
    
    # Test 3: Get observation
    print("\n[3] Testing observation...")
    obs = client.get_observation()
    if obs:
        print(f"    ✓ Position: ({obs['position']['x']:.1f}, {obs['position']['y']:.1f}, {obs['position']['z']:.1f})")
        print(f"    ✓ Health: {obs['health']}")
        print(f"    ✓ Food: {obs['food']}")
    else:
        print("    ✗ Failed to get observation")
        return 1
    
    # Test 4: Reset episode
    print("\n[4] Testing reset...")
    result = client.reset()
    if "observation" in result:
        print("    ✓ Episode reset successful")
    else:
        print(f"    ✗ Reset failed: {result.get('error')}")
        return 1
    
    # Test 5: Execute actions
    print("\n[5] Testing actions...")
    
    actions = [
        {"type": "move", "direction": "forward", "duration": 2},
        {"type": "jump"},
        {"type": "look", "yaw": 0.5, "pitch": 0},
        {"type": "move", "direction": "back", "duration": 1},
    ]
    
    for i, action in enumerate(actions):
        result = client.step(action)
        if result.get("observation"):
            pos = result["observation"]["position"]
            reward = result.get("reward", 0)
            print(f"    ✓ Action {i+1} ({action['type']}): pos=({pos['x']:.1f}, {pos['y']:.1f}, {pos['z']:.1f}), reward={reward:.4f}")
        else:
            print(f"    ✗ Action {i+1} failed: {result.get('error')}")
        time.sleep(0.2)
    
    # Final status
    print("\n[6] Final status...")
    status = client.get_status()
    print(f"    ✓ Total steps: {status.get('stepCount')}")
    print(f"    ✓ Total reward: {status.get('totalReward', 0):.4f}")
    print(f"    ✓ Visited blocks: {status.get('visitedBlocks')}")
    
    print()
    print("=" * 50)
    print("✅ All bridge tests passed!")
    print("=" * 50)
    
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())