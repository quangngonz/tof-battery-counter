"""
Test for statistics endpoint
"""

import requests
from .config import API_BASE_URL


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
