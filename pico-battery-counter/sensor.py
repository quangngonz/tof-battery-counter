import machine
import utime


class IRSensor:
    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.last = self.pin.value()
        self.last_trigger = 0

    def check(self):
        now = utime.ticks_ms()
        current = self.pin.value()

        # detect falling edge + debounce
        if self.last == 1 and current == 0:
            if now - self.last_trigger > 150:
                self.last_trigger = now
                self.last = current
                return True

        self.last = current
        return False
