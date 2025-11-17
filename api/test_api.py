#!/usr/bin/env python3
"""
Test script to simulate sending data to the Battery Counter API
"""

import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")


def test_root():
    """Test the root endpoint"""
    print("Testing GET / ...")
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
    return response.status_code == 200


def test_log_battery(amount=1, device_id="test_device"):
    """Test logging a battery count"""
    print(f"Testing POST /log (amount={amount}, device_id={device_id}) ...")

    timestamp = int(time.time())
    payload = {
        "timestamp": timestamp,
        "amount": amount,
        "device_id": device_id
    }

    response = requests.post(
        f"{API_BASE_URL}/log",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_get_stats():
    """Test getting battery statistics"""
    print("Testing GET /stats ...")
    response = requests.get(f"{API_BASE_URL}/stats")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response:")
        print(f"  Total batteries: {data.get('total', 0)}")
        print(f"  Soil (kg): {data.get('soil', 0)}")
        print(f"  Water (L): {data.get('water', 0)}\n")
    else:
        print(f"Response: {response.text}\n")

    return response.status_code == 200


def run_all_tests():
    """Run all API tests"""
    print("=" * 50)
    print("Battery Counter API Test Suite")
    print("=" * 50 + "\n")

    results = []

    # Test 1: Root endpoint
    results.append(("Root endpoint", test_root()))

    # Test 2: Log a single battery
    results.append(("Log single battery", test_log_battery(
        amount=1, device_id="test_pico")))

    # Test 3: Log multiple batteries
    results.append(("Log multiple batteries", test_log_battery(
        amount=5, device_id="test_pico")))

    # Test 4: Get statistics
    results.append(("Get statistics", test_get_stats()))

    # Print summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
