from ili9341 import Display
import utime


# TODO: Make unit conversion constants configurable and document units.
# TODO: Support multiple display drivers or provide a factory for initialization.
class TFT:
    SOIL = 0.02
    WATER = 0.15

    def __init__(self, display):
        # TODO: Consider validating `display` to ensure required methods exist.
        self.display = display

    def show(self, total):
        # TODO: Consider defensive checks for `total` being numeric.
        soil = total * self.SOIL
        water = total * self.WATER

        self.display.clear()

        # TODO: Add localization/formatting options and font sizing for readability.
        self.display.draw_text(10, 20, f"Batteries: {total}")
        self.display.draw_text(10, 60, f"Soil saved: {soil:.2f} m2")
        self.display.draw_text(10, 100, f"Water saved: {water:.1f} L")
