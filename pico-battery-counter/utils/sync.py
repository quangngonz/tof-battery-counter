"""
Sync Module for Cache Management and Cloud API Integration
Handles local caching, internet connectivity, and background syncing
"""

import json
import time
import requests
import subprocess
import threading
from pathlib import Path
from config import (
    API_LOG, API_STATS, DEVICE_ID, CACHE_FILE,
    WIFI_CHECK_HOST, SYNC_INTERVAL_SECONDS
)

# Thread-safe cache access lock
_cache_lock = threading.Lock()

# Cache Management Functions


def load_cache():
    """
    Load cached records from JSON file

    Returns:
        list: List of cached records, empty list if file doesn't exist
    """
    with _cache_lock:
        cache_path = Path(CACHE_FILE)
        if not cache_path.exists():
            return []

        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading cache: {e}")
            return []


def save_cache(data):
    """
    Save records to cache file

    Args:
        data: List of records to save
    """
    with _cache_lock:
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving cache: {e}")


def add_record():
    """
    Add a new battery count record to the cache
    """
    record = {
        "timestamp": int(time.time()),
        "amount": 1,
        "device": DEVICE_ID
    }

    cache = load_cache()
    cache.append(record)
    save_cache(cache)
    print(f"Record added to cache: {record}")


# Network Functions

def has_internet():
    """
    Check if internet connection is available via ping

    Returns:
        bool: True if internet is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', WIFI_CHECK_HOST],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception) as e:
        return False


def fetch_stats():
    """
    Fetch statistics from the cloud API

    Returns:
        dict: Statistics with keys 'total', 'soil', 'water', or None if failed
    """
    if not has_internet():
        return None

    try:
        response = requests.get(API_STATS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Ensure required keys exist
            return {
                "total": data.get("total", 0),
                "soil": data.get("soil", 0),
                "water": data.get("water", 0)
            }
    except (requests.RequestException, json.JSONDecodeError, Exception) as e:
        print(f"Error fetching stats: {e}")

    return None


# Background Sync Thread

_sync_thread = None
_sync_running = False

# Shared stats - updated by sync service, read by detection service
_latest_stats = {
    "total": 0,
    "soil": 0,
    "water": 0
}
_stats_lock = threading.Lock()


def get_latest_stats():
    """
    Get the latest stats (non-blocking, no network call)

    Returns:
        dict: Latest stats cached from API
    """
    with _stats_lock:
        return _latest_stats.copy()


def _sync_worker():
    """
    Background worker that continuously syncs cached records to the API
    and refreshes stats periodically
    """
    global _sync_running, _latest_stats

    print("Sync thread started")

    while _sync_running:
        try:
            # Check internet connectivity
            if has_internet():
                # Fetch fresh stats from API (non-blocking for detection service)
                new_stats = fetch_stats()
                if new_stats is not None:
                    with _stats_lock:
                        _latest_stats = new_stats
                    print(f"Stats refreshed: {_latest_stats}")

                # Sync cached records
                cache = load_cache()

                if cache:
                    print(f"Syncing {len(cache)} cached records...")
                    updated_cache = []

                    for record in cache:
                        try:
                            # Attempt to POST record to API
                            response = requests.post(
                                API_LOG,
                                json=record,
                                timeout=5
                            )

                            if response.status_code == 200:
                                print(f"Synced record: {record['timestamp']}")
                                # Successfully synced, don't keep it
                            else:
                                print(
                                    f"Failed to sync record (status {response.status_code})")
                                updated_cache.append(record)

                        except requests.RequestException as e:
                            print(f"Error syncing record: {e}")
                            updated_cache.append(record)

                    # Reload cache to preserve any records added during sync
                    current_cache = load_cache()
                    # Get timestamps of records that failed to sync (still need to retry)
                    failed_timestamps = set(r['timestamp']
                                            for r in updated_cache)
                    # Get timestamps of original records we attempted to sync
                    attempted_timestamps = set(r['timestamp'] for r in cache)

                    # Keep records that either:
                    # 1. Failed to sync (in failed_timestamps), OR
                    # 2. Were added during sync (NOT in attempted_timestamps)
                    final_cache = [
                        r for r in current_cache
                        if r['timestamp'] in failed_timestamps or r['timestamp'] not in attempted_timestamps
                    ]

                    # Save updated cache (only successfully synced records removed)
                    save_cache(final_cache)

                    if len(final_cache) < len(cache):
                        print(
                            f"Sync complete. {len(final_cache)} records remain in cache.")

        except Exception as e:
            print(f"Sync thread error: {e}")

        # Sleep before next sync attempt
        time.sleep(SYNC_INTERVAL_SECONDS)

    print("Sync thread stopped")


def start_sync_thread():
    """
    Start the background sync thread
    """
    global _sync_thread, _sync_running

    if _sync_thread is not None and _sync_thread.is_alive():
        print("Sync thread already running")
        return

    _sync_running = True
    _sync_thread = threading.Thread(target=_sync_worker, daemon=True)
    _sync_thread.start()


def stop_sync_thread():
    """
    Stop the background sync thread
    """
    global _sync_running
    _sync_running = False
