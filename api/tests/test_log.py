"""
Test for battery logging endpoint
"""

import requests
import time
from .config import API_BASE_URL


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
