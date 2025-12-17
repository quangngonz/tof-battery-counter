#!/usr/bin/env python3
"""
Main application for Raspberry Pi 4 battery counter
Orchestrates two independent services:
  1. Detection Service - Monitors sensor and updates display (non-blocking)
  2. Sync Service - Syncs cached records to cloud (background)
"""

import RPi.GPIO as GPIO
import signal
import sys
import time

from utils.detection import DetectionService
from utils.sync import start_sync_thread, stop_sync_thread


# Global service instances
detection_service = None


def cleanup_handler(signum, frame):
    """
    Handle cleanup on exit signals
    """
    print("\n\nShutting down gracefully...")

    # Stop both services
    if detection_service is not None:
        detection_service.stop()
    stop_sync_thread()

    # Cleanup GPIO
    GPIO.cleanup()

    print("Shutdown complete")
    sys.exit(0)


def main():
    """
    Main application - starts both services and waits
    """
    global detection_service

    print("=" * 50)
    print("Battery Counter - Raspberry Pi 4")
    print("Two-Service Architecture")
    print("=" * 50)

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)

    # Start Service 1: Background Sync
    print("\n[Service 1] Starting sync service...")
    start_sync_thread()

    # Start Service 2: Detection & Display
    print("\n[Service 2] Starting detection service...")
    detection_service = DetectionService()
    detection_service.start()

    print("\n" + "=" * 50)
    print("Both services running independently!")
    print("Press Ctrl+C to stop")
    print("=" * 50 + "\n")

    # Keep main thread alive - services run independently
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup_handler(None, None)


if __name__ == "__main__":
    main()
