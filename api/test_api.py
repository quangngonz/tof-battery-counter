#!/usr/bin/env python3
"""
Test script to simulate sending data to the Battery Counter API
"""

import requests
from tests.runner import run_all_tests

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
