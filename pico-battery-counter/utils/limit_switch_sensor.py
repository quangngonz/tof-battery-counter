"""
Limit Switch Sensor Module for Raspberry Pi
Handles GPIO-based limit switch detection
"""

import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from config import LIMIT_SWITCH_PIN, DEBOUNCE_MS


class LimitSwitchSensor:
    """
    Limit Switch Sensor for Battery Detection
    Simple GPIO-based detection with debouncing
    """

    def __init__(self, pin=LIMIT_SWITCH_PIN, debounce_ms=DEBOUNCE_MS):
        """
        Initialize limit switch sensor

        Args:
            pin: GPIO pin number (BCM numbering)
            debounce_ms: Debounce time in milliseconds
        """
        self.pin = pin
        self.debounce_time = debounce_ms / 1000.0  # Convert to seconds
        self.last_trigger_time = 0
        self.last_state = False  # False = not pressed, True = pressed

        if GPIO is None:
            raise RuntimeError("RPi.GPIO module not available")

        # Setup GPIO pin with pull-up resistor
        # Assumes switch connects pin to ground when pressed
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(
            f"Limit Switch: Initialized on GPIO {self.pin} with {debounce_ms}ms debounce")

    def read_state(self):
        """
        Read the current state of the limit switch

        Returns:
            bool: True if switch is pressed, False otherwise
        """
        # GPIO.LOW means switch is pressed (pulls pin to ground)
        return GPIO.input(self.pin) == GPIO.LOW

    def check(self):
        """
        Check if limit switch has been triggered (pressed)
        Includes debouncing logic to prevent false triggers

        Returns:
            bool: True if a new press is detected, False otherwise
        """
        current_time = time.time()
        current_state = self.read_state()

        # Check for state change from not pressed to pressed
        if current_state and not self.last_state:
            # Check debounce
            if current_time - self.last_trigger_time >= self.debounce_time:
                self.last_trigger_time = current_time
                self.last_state = current_state
                print(f"Limit Switch: PRESSED (GPIO {self.pin})")
                return True

        # Update state
        self.last_state = current_state
        return False

    def cleanup(self):
        """
        Cleanup GPIO resources
        """
        # GPIO cleanup is typically handled globally
        pass
