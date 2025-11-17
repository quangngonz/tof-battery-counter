from ili9341 import Display
import utime


class TFT:
    def __init__(self, display):
        self.display = display

    def show(self, total, soil, water):
        """Display battery stats. Values should come from server + unsynced calculations."""
        self.display.clear()

        self.display.draw_text(10, 20, f"Batteries: {total}")
        self.display.draw_text(10, 60, f"Soil saved: {soil:.2f} kg")
        self.display.draw_text(10, 100, f"Water saved: {water:.1f} L")
