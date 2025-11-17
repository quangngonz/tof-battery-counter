import network
import utime
import urequests
import json
import os
from config import SSID, PASS, API_LOG, API_STATS, DEVICE_ID

CACHE_FILE = "cache.json"


def load_cache():
    if CACHE_FILE not in os.listdir():
        return []
    with open(CACHE_FILE) as f:
        return json.loads(f.read())


def save_cache(c):
    with open(CACHE_FILE, "w") as f:
        f.write(json.dumps(c))


def add_record():
    cache = load_cache()
    cache.append({
        "timestamp": utime.time(),
        "amount": 1,
        "device_id": DEVICE_ID
    })
    save_cache(cache)


WIFI_TIMEOUT_SEC = 8


def connect_wifi():
    """Connect to WiFi with timeout."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True

    wlan.connect(SSID, PASS)
    for _ in range(WIFI_TIMEOUT_SEC):
        if wlan.isconnected():
            print('WiFi connected')
            return True
        utime.sleep(1)
    print('WiFi connection failed')
    return False


def sync():
    """Sync cached records to server."""
    if not connect_wifi():
        return False

    cache = load_cache()
    if not cache:
        return True

    for entry in cache[:]:
        try:
            response = urequests.post(API_LOG, json=entry)
            success = response.status_code == 200
            response.close()
            if success:
                cache.remove(entry)
                save_cache(cache)
                print(f'Synced 1 record, {len(cache)} remaining')
            else:
                print(f'Sync failed with status {response.status_code}')
                return False
        except Exception as e:
            print(f'Sync error: {e}')
            return False

    return True


def fetch_stats():
    """Fetch statistics from server."""
    if not connect_wifi():
        return None
    try:
        response = urequests.get(API_STATS)
        data = response.json()
        response.close()
        return data
    except Exception as e:
        print(f'Fetch stats error: {e}')
        return None
