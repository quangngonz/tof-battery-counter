"""
Test for root endpoint
"""

import requests
from .config import API_BASE_URL


def test_root():
    """Test the root endpoint"""
    print("Testing GET / ...")
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
    return response.status_code == 200
