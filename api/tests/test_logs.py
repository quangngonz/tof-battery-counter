"""
Test for logs retrieval endpoint
"""

import requests
from .config import API_BASE_URL


def test_get_logs():
    """Test getting battery logs"""
    print("Testing GET /logs ...")
    response = requests.get(f"{API_BASE_URL}/logs")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response: Retrieved {len(data)} logs")
        if data:
            print(f"  Latest log: {data[0]}")
        print()
    else:
        print(f"Response: {response.text}\n")

    return response.status_code == 200
