"""
Detection Service for Battery Counter
Runs in its own thread to monitor sensor and update display without blocking
"""

import RPi.GPIO as GPIO
import time
import threading
from config import LED_PIN, MAIN_LOOP_SLEEP, STATS_UPDATE_INTERVAL_LOOPS, SHOW_DISTANCE_MEASUREMENT
from utils.sync import add_record, get_latest_stats, load_cache
from utils.st7789_display import TFT
from utils.limit_switch_sensor import LimitSwitchSensor


class DetectionService:
    """
    Independent service for battery detection and display updates
    Runs in its own thread for maximum responsiveness
    """

    def __init__(self):
        self.running = False
        self.thread = None
        self.sensor = None
        self.tft = None
        self.loop_counter = 0

        # Stats tracking
        self.last_stats = {
            "total": 0,
            "soil": 0,
            "water": 0
        }

        # High water marks - never show values lower than these
        self.max_total_shown = 0
        self.max_soil_shown = 0.0
        self.max_water_shown = 0.0

    def _initialize_hardware(self):
        """Initialize GPIO, sensor, LED, and display"""
        print("\nInitializing detection hardware...")

        # Set GPIO mode (BCM numbering)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Initialize limit switch sensor
        self.sensor = LimitSwitchSensor()

        # Initialize LED
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        print(f"LED initialized on GPIO {LED_PIN}")

        # Initialize TFT display (optional)
        try:
            self.tft = TFT(show_distance=SHOW_DISTANCE_MEASUREMENT)
        except Exception as e:
            print(f"Display initialization failed: {e}")
            print("Continuing without display...")
            self.tft = None

    def _update_display(self, current_distance=-1):
        """
        Update display with current stats + unsynced records
        Always applies high water mark to prevent decreasing values
        """
        if self.tft is None:
            return

        # Calculate display values including unsynced records
        unsynced = len(load_cache())
        total_display = self.last_stats["total"] + unsynced
        soil_display = self.last_stats["soil"] + (unsynced * 1)
        water_display = self.last_stats["water"] + (unsynced * 500)

        # Apply high water mark - never decrease
        total_display = max(total_display, self.max_total_shown)
        soil_display = max(soil_display, self.max_soil_shown)
        water_display = max(water_display, self.max_water_shown)

        # Update high water marks
        self.max_total_shown = total_display
        self.max_soil_shown = soil_display
        self.max_water_shown = water_display

        # Update display
        self.tft.show(total_display, soil_display,
                      water_display, current_distance)

    def _detection_loop(self):
        """Main detection loop - runs independently"""
        print("\n" + "=" * 50)
        print("Detection service ready! Monitoring sensor...")
        print("=" * 50 + "\n")

        current_distance = -1

        try:
            while self.running:
                # Turn LED on during active monitoring
                GPIO.output(LED_PIN, GPIO.HIGH)

                # Check for limit switch press
                if self.sensor.check():
                    print(f"\n*** BATTERY DETECTED! ***")

                    # Add record to cache
                    add_record()

                    # INSTANT DISPLAY UPDATE - No waiting!
                    self._update_display(current_distance)
                    print(f"Display updated instantly!")

                    # Brief LED blink to indicate detection
                    GPIO.output(LED_PIN, GPIO.LOW)
                    time.sleep(0.1)
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    time.sleep(0.1)

                # Periodic display update with latest stats (non-blocking)
                if self.loop_counter % STATS_UPDATE_INTERVAL_LOOPS == 0:
                    # Get latest stats from sync service (no network call!)
                    self.last_stats = get_latest_stats()

                    # Update display with latest stats
                    self._update_display(current_distance)

                    unsynced = len(load_cache())
                    print(
                        f"Display updated: Total={self.max_total_shown}, Unsynced={unsynced}")

                # Turn LED off
                GPIO.output(LED_PIN, GPIO.LOW)

                # Increment loop counter
                self.loop_counter += 1

                # Non-blocking sleep
                time.sleep(MAIN_LOOP_SLEEP)

        except Exception as e:
            print(f"Detection loop error: {e}")
        finally:
            print("Detection loop stopped")

    def start(self):
        """Start the detection service thread"""
        if self.thread is not None and self.thread.is_alive():
            print("Detection service already running")
            return

        self._initialize_hardware()

        self.running = True
        self.thread = threading.Thread(
            target=self._detection_loop, daemon=True)
        self.thread.start()
        print("Detection service started")

    def stop(self):
        """Stop the detection service thread"""
        print("Stopping detection service...")
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
