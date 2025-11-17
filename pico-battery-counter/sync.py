"""Synchronization module for Raspberry Pi using standard Python libraries"""
import requests
import json
import os
import time
from pathlib import Path
from config import API_LOG, API_STATS, DEVICE_ID, CACHE_FILE


def load_cache():
    """
    Load cached records from JSON file.

    Returns:
        list: List of cached battery detection records
    """
    cache_path = Path(CACHE_FILE)

    # Ensure directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if not cache_path.exists():
        return []

    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f'Error loading cache: {e}')
        return []


def save_cache(cache_data):
    """
    Save cache data to JSON file.

    Args:
        cache_data: List of records to save
    """
    cache_path = Path(CACHE_FILE)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except IOError as e:
        print(f'Error saving cache: {e}')


def add_record():
    """
    Add a new battery detection record to the cache.
    Records are timestamped and include device ID.
    """
    cache = load_cache()
    cache.append({
        "timestamp": int(time.time()),
        "amount": 1,
        "device_id": DEVICE_ID
    })
    save_cache(cache)


def sync():
    """
    Sync cached records to server via HTTP POST.
    Network connectivity is assumed (handled by Raspberry Pi OS).

    Returns:
        bool: True if all records synced successfully, False otherwise
    """
    cache = load_cache()
    if not cache:
        return True

    for entry in cache[:]:
        try:
            response = requests.post(
                API_LOG,
                json=entry,
                timeout=10
            )

            if response.status_code == 200:
                cache.remove(entry)
                save_cache(cache)
                print(f'Synced 1 record, {len(cache)} remaining')
            else:
                print(f'Sync failed with status {response.status_code}')
                return False

        except requests.exceptions.RequestException as e:
            print(f'Sync error: {e}')
            return False

    return True


def fetch_stats():
    """
    Fetch battery statistics from server via HTTP GET.

    Returns:
        dict: Statistics data (total, soil, water) or None if request fails
    """
    try:
        response = requests.get(API_STATS, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            print(f'Fetch stats failed with status {response.status_code}')
            return None

    except requests.exceptions.RequestException as e:
        print(f'Fetch stats error: {e}')
        return None
