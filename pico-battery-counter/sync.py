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


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True

    wlan.connect(SSID, PASS)
    for _ in range(8):
        if wlan.isconnected():
            return True
        utime.sleep(1)
    return False


def sync():
    if not connect_wifi():
        return False

    cache = load_cache()
    if not cache:
        return True

    for entry in cache[:]:
        try:
            r = urequests.post(API_LOG, json=entry)
            ok = r.status_code == 200
            r.close()
            if ok:
                cache.remove(entry)
                save_cache(cache)
            else:
                return False
        except:
            return False

    return True


def fetch_stats():
    if not connect_wifi():
        return None
    try:
        r = urequests.get(API_STATS)
        data = r.json()
        r.close()
        return data
    except:
        return None
