"""
IR Sensor Module for Raspberry Pi
Handles GPIO setup and debounced beam break detection
"""

import RPi.GPIO as GPIO
import time
from config import IR_PIN, DEBOUNCE_MS


class IRSensor:
    """
    Non-blocking IR sensor with software debouncing
    """

    def __init__(self, pin=IR_PIN):
        """
        Initialize the IR sensor on the specified GPIO pin

        Args:
            pin: GPIO pin number (BCM numbering)
        """
        self.pin = pin
        self.last_trigger_time = 0
        self.debounce_time = DEBOUNCE_MS / 1000.0  # Convert to seconds
        self.last_state = GPIO.HIGH

        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        print(f"IR Sensor initialized on GPIO {self.pin}")

    def check(self):
        """
        Non-blocking check for IR beam break event

        Returns:
            bool: True if a new beam break event is detected, False otherwise
        """
        current_time = time.monotonic()
        current_state = GPIO.input(self.pin)

        # Detect falling edge (beam interrupted: HIGH -> LOW)
        if self.last_state == GPIO.HIGH and current_state == GPIO.LOW:
            # Check debounce timing
            if (current_time - self.last_trigger_time) >= self.debounce_time:
                self.last_trigger_time = current_time
                self.last_state = current_state
                return True

        self.last_state = current_state
        return False

    def cleanup(self):
        """
        Clean up GPIO resources
        """
        GPIO.cleanup(self.pin)
