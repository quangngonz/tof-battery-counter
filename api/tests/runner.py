"""
Test runner for Battery Counter API
"""

import requests
from .test_root import test_root
from .test_log import test_log_battery
from .test_logs import test_get_logs
from .test_stats import test_get_stats


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

    # Test 4: Get logs
    results.append(("Get logs", test_get_logs()))

    # Test 5: Get statistics
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
