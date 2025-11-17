"""IR Sensor module for Raspberry Pi using RPi.GPIO"""
import RPi.GPIO as GPIO
import time


class IRSensor:
    DEBOUNCE_MS = 150  # Debounce time in milliseconds

    def __init__(self, pin):
        """
        Initialize IR sensor on specified GPIO pin (BCM numbering).

        Args:
            pin: GPIO pin number (BCM numbering)
        """
        self.pin = pin

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.last_value = GPIO.input(self.pin)
        self.last_trigger = 0

    def check(self):
        """
        Check for sensor trigger with debouncing.
        Detects falling edge (1 -> 0) which indicates object detected.

        Returns:
            bool: True if sensor was triggered, False otherwise
        """
        now = time.time() * 1000  # Convert to milliseconds
        current_value = GPIO.input(self.pin)

        # Detect falling edge (1 -> 0) with debounce
        if self.last_value == 1 and current_value == 0:
            if (now - self.last_trigger) > self.DEBOUNCE_MS:
                self.last_trigger = now
                self.last_value = current_value
                return True

        self.last_value = current_value
        return False

    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup(self.pin)
