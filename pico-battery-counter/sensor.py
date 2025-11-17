import machine
import utime


class IRSensor:
    DEBOUNCE_MS = 150  # Debounce time in milliseconds

    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.last_value = self.pin.value()
        self.last_trigger = 0

    def check(self):
        """Check for sensor trigger with debouncing."""
        now = utime.ticks_ms()
        current_value = self.pin.value()

        # Detect falling edge (1 -> 0) with debounce
        if self.last_value == 1 and current_value == 0:
            if utime.ticks_diff(now, self.last_trigger) > self.DEBOUNCE_MS:
                self.last_trigger = now
                self.last_value = current_value
                return True

        self.last_value = current_value
        return False
