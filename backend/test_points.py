#!/usr/bin/env python3
"""
Test script for the points system
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_points_system():
    print("🧪 Testing Points System")
    print("=" * 50)
    
    # Test 1: Get exercise configs
    print("\n1. Testing exercise configs...")
    try:
        response = requests.get(f"{BASE_URL}/points/config")
        if response.status_code == 200:
            configs = response.json()
            print("✅ Exercise configs loaded successfully")
            print(f"Available exercises: {list(configs['exercise_configs'].keys())}")
        else:
            print(f"❌ Failed to get configs: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting configs: {e}")
        return
    
    # Test 2: Test points calculation logic
    print("\n2. Testing points calculation logic...")
    exercise_configs = configs['exercise_configs']
    
    test_cases = [
        ("squat", 15, 1),  # 15 reps = 1 cycle = 15 points
        ("squat", 30, 2),  # 30 reps = 2 cycles = 30 points
        ("squat", 20, 1),  # 20 reps = 1 cycle = 15 points
        ("push-up", 10, 1),  # 10 reps = 1 cycle = 10 points
        ("burpee", 8, 1),   # 8 reps = 1 cycle = 16 points
    ]
    
    for exercise, reps, expected_cycles in test_cases:
        config = exercise_configs[exercise]
        reps_per_cycle = config["reps_per_cycle"]
        points_per_cycle = config["points_per_cycle"]
        cycles_completed = reps // reps_per_cycle
        points_earned = cycles_completed * points_per_cycle
        
        print(f"   {exercise}: {reps} reps → {cycles_completed} cycles → {points_earned} points")
        
        if cycles_completed == expected_cycles:
            print(f"   ✅ Correct calculation")
        else:
            print(f"   ❌ Expected {expected_cycles} cycles, got {cycles_completed}")
    
    print("\n✅ Points system logic test completed!")

if __name__ == "__main__":
    test_points_system() 