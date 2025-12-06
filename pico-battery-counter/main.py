#!/usr/bin/env python3
"""
Main application for Raspberry Pi 4 battery counter
Counts IR beam breaks, caches events, syncs to cloud, and displays statistics
"""

import RPi.GPIO as GPIO
import time
import signal
import sys

# Import project modules
from config import LED_PIN, MAIN_LOOP_SLEEP, STATS_UPDATE_INTERVAL_LOOPS, SHOW_DISTANCE_MEASUREMENT
from utils.sync import add_record, start_sync_thread, stop_sync_thread, fetch_stats, load_cache
from utils.st7789_display import TFT
from utils.tof_sensor import TOFSensor


def cleanup_handler(signum, frame):
    """
    Handle cleanup on exit signals
    """
    print("\nShutting down gracefully...")
    stop_sync_thread()
    GPIO.cleanup()
    sys.exit(0)


def main():
    """
    Main application loop
    """
    print("=" * 50)
    print("Battery Counter - Raspberry Pi 4")
    print("=" * 50)

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)

    # Initialize hardware
    print("\nInitializing hardware...")

    # Set GPIO mode first (BCM numbering)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initialize TOF sensor
    sensor = TOFSensor()

    # Initialize LED
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)
    print(f"LED initialized on GPIO {LED_PIN}")

    # Initialize TFT display (optional)
    try:
        tft = TFT(show_distance=SHOW_DISTANCE_MEASUREMENT)
    except Exception as e:
        print(f"Display initialization failed: {e}")
        print("Continuing without display...")
        tft = None

    # Start background sync thread
    print("\nStarting background sync thread...")
    start_sync_thread()

    # Application state
    loop_counter = 0
    last_stats = {
        "total": 0,
        "soil": 0,
        "water": 0
    }
    local_detections = 0  # Track detections since last sync to prevent double-counting

    print("\n" + "=" * 50)
    print("System ready! Monitoring TOF sensor...")
    print("=" * 50 + "\n")

    # Main loop
    try:
        current_distance = -1
        while True:
            # Turn LED on during active monitoring
            GPIO.output(LED_PIN, GPIO.HIGH)

            # Read current distance from TOF sensor
            current_distance = sensor.read_distance()

            # Check for TOF object detection
            if sensor.check():
                print(f"\n*** BATTERY DETECTED! ***")
                add_record()
                local_detections += 1

                # INSTANT TFT UPDATE - User sees it immediately!
                if tft is not None:
                    # Calculate instant display values
                    unsynced = len(load_cache())
                    total_display = last_stats["total"] + unsynced
                    soil_display = last_stats["soil"] + (unsynced * 1)
                    water_display = last_stats["water"] + (unsynced * 500)

                    print(
                        f"Instant update: Total={total_display}, Soil={soil_display:.2f}m3, Water={water_display:.2f}L")
                    tft.show(total_display, soil_display,
                             water_display, current_distance)

                # Brief LED blink to indicate detection
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.1)

            # Periodic stats update
            if loop_counter % STATS_UPDATE_INTERVAL_LOOPS == 0:
                # Fetch fresh stats from API
                new_stats = fetch_stats()
                if new_stats is not None:
                    # Check if server has caught up with our local detections
                    server_increase = new_stats["total"] - last_stats["total"]

                    # Neutralize local detections that have been synced
                    if server_increase >= local_detections:
                        # Server has all our detections, reset counter
                        local_detections = 0
                    else:
                        # Server hasn't caught up yet, adjust counter
                        local_detections -= server_increase

                    last_stats = new_stats
                    print(f"\nStats updated from API: {last_stats}")
                    print(f"Local detections pending sync: {local_detections}")

                # Calculate display values including unsynced records
                unsynced = len(load_cache())
                total_display = last_stats["total"] + unsynced
                soil_display = last_stats["soil"] + (unsynced * 1)
                water_display = last_stats["water"] + (unsynced * 500)

                print(
                    f"Display values: Total={total_display}, Soil={soil_display:.2f}m3, Water={water_display:.2f}L")
                print(f"Unsynced records: {unsynced}")

                # Update TFT display if available
                if tft is not None:
                    tft.show(total_display, soil_display,
                             water_display, current_distance)

            # Turn LED off
            GPIO.output(LED_PIN, GPIO.LOW)

            # Increment loop counter
            loop_counter += 1

            # Non-blocking sleep
            time.sleep(MAIN_LOOP_SLEEP)

    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt received...")
        cleanup_handler(None, None)

    except Exception as e:
        print(f"\n\nUnexpected error in main loop: {e}")
        cleanup_handler(None, None)


if __name__ == "__main__":
    main()
