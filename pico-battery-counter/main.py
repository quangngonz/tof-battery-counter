#!/usr/bin/env python3
"""
Main program for Battery Counter with IR sensor and cloud sync.
Raspberry Pi 4 / Raspberry Pi Zero 2 version.
"""
import time
import signal
import sys
import RPi.GPIO as GPIO
from sensor import IRSensor
from sync import add_record, sync, fetch_stats, load_cache
from tft import TFT
import config

# Constants
LOOP_DELAY_MS = 50
STATS_FETCH_INTERVAL = 100

# Global cleanup flag
cleanup_done = False


def cleanup_handler(signum, frame):
    """Handle cleanup on exit."""
    global cleanup_done
    if cleanup_done:
        return

    cleanup_done = True
    print('\nShutting down Battery Counter...')

    # Clean up GPIO
    try:
        GPIO.cleanup()
    except Exception as e:
        print(f'GPIO cleanup error: {e}')

    # Clean up display
    try:
        if tft:
            tft.cleanup()
    except Exception as e:
        print(f'Display cleanup error: {e}')

    print('Cleanup complete')
    sys.exit(0)


# Register signal handlers for clean shutdown
signal.signal(signal.SIGINT, cleanup_handler)
signal.signal(signal.SIGTERM, cleanup_handler)


def main():
    """Main application loop."""
    global tft

    print('Battery Counter for Raspberry Pi')
    print('=' * 40)
    print(f'Device ID: {config.DEVICE_ID}')
    print(f'IR Sensor: GPIO{config.IR_PIN}')
    print(f'LED: GPIO{config.LED_PIN}')
    print('=' * 40)

    # Initialize hardware
    try:
        sensor = IRSensor(config.IR_PIN)
        print('✓ IR Sensor initialized')
    except Exception as e:
        print(f'✗ Failed to initialize IR sensor: {e}')
        sys.exit(1)

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.LED_PIN, GPIO.OUT)
        print('✓ LED initialized')
    except Exception as e:
        print(f'✗ Failed to initialize LED: {e}')
        sys.exit(1)

    try:
        tft = TFT()
        print('✓ Display initialized')
        # Show startup message
        tft.show(0, 0.0, 0.0)
    except Exception as e:
        print(f'✗ Failed to initialize display: {e}')
        print('  Continuing without display...')
        tft = None

    # State variables
    last_server_stats = {'total': 0, 'soil': 0, 'water': 0}
    loop_counter = 0

    print('\nBattery Counter started - monitoring for batteries...\n')

    try:
        while True:
            # Turn on status LED
            GPIO.output(config.LED_PIN, GPIO.HIGH)

            # Check for sensor trigger
            if sensor.check():
                add_record()
                print('Battery detected and logged')

            # Sync cached records to server
            sync()

            # Fetch server stats periodically to reduce API calls
            if loop_counter >= STATS_FETCH_INTERVAL:
                data = fetch_stats()
                if data:
                    last_server_stats = data

                loop_counter = 0

            # Calculate total including unsynced records
            unsynced_count = len(load_cache())
            total_display = last_server_stats.get('total', 0) + unsynced_count
            soil_display = last_server_stats.get(
                'soil', 0) + (unsynced_count * 0.02)
            water_display = last_server_stats.get(
                'water', 0) + (unsynced_count * 0.15)

            # Update display if available
            if tft:
                try:
                    tft.show(total_display, soil_display, water_display)
                except Exception as e:
                    print(f'Display error: {e}')

            # Small delay and turn off LED
            time.sleep(LOOP_DELAY_MS / 1000.0)
            GPIO.output(config.LED_PIN, GPIO.LOW)

            loop_counter += 1

    except KeyboardInterrupt:
        cleanup_handler(None, None)
    except Exception as e:
        print(f'Fatal error: {e}')
        cleanup_handler(None, None)


if __name__ == '__main__':
    main()
