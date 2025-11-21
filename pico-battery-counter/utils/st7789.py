"""
ST7789 Display Driver for Raspberry Pi 4
Supports 240x320 and other ST7789 displays
"""

import time
import struct

# ST7789 Commands
_SWRESET = 0x01
_SLPOUT = 0x11
_COLMOD = 0x3A
_MADCTL = 0x36
_CASET = 0x2A
_RASET = 0x2B
_RAMWR = 0x2C
_INVON = 0x21
_INVOFF = 0x20
_DISPON = 0x29
_DISPOFF = 0x28


class ST7789:
    def __init__(self, spi, width, height, reset, dc, cs, backlight=None, rotation=0):
        self.spi = spi
        self.width = width
        self.height = height
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight

        # Initialize pins
        self.reset.on()
        self.dc.off()
        if self.cs:
            self.cs.on()

        if self.backlight:
            self.backlight.on()

        # Initialize display
        self._init_display()
        self.set_rotation(rotation)

    def _write_cmd(self, cmd):
        """Write command to display"""
        if self.cs:
            self.cs.off()
        self.dc.off()
        self.spi.writebytes([cmd])
        if self.cs:
            self.cs.on()

    def _write_data(self, data):
        """Write data to display"""
        if self.cs:
            self.cs.off()
        self.dc.on()
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)
        if self.cs:
            self.cs.on()

    def _init_display(self):
        """Initialize the ST7789 display"""
        # Hardware reset
        self.reset.off()
        time.sleep(0.05)
        self.reset.on()
        time.sleep(0.05)

        # Software reset
        self._write_cmd(_SWRESET)
        time.sleep(0.15)

        # Sleep out
        self._write_cmd(_SLPOUT)
        time.sleep(0.12)

        # Color mode - 16-bit color (RGB565)
        self._write_cmd(_COLMOD)
        self._write_data(0x55)

        # Display inversion on
        self._write_cmd(_INVON)

        # Display on
        self._write_cmd(_DISPON)
        time.sleep(0.1)

    def set_rotation(self, rotation):
        """Set display rotation (0, 1, 2, 3)"""
        self._write_cmd(_MADCTL)
        if rotation == 0:
            self._write_data(0x00)
        elif rotation == 1:
            self._write_data(0x60)
        elif rotation == 2:
            self._write_data(0xC0)
        elif rotation == 3:
            self._write_data(0xA0)

    def set_window(self, x0, y0, x1, y1):
        """Set the pixel address window for drawing"""
        # Column address
        self._write_cmd(_CASET)
        self._write_data(bytearray([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))

        # Row address
        self._write_cmd(_RASET)
        self._write_data(bytearray([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))

        # Write to RAM
        self._write_cmd(_RAMWR)

    def pixel(self, x, y, color):
        """Draw a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.set_window(x, y, x, y)
            self._write_data(bytearray([color >> 8, color & 0xFF]))

    def fill(self, color):
        """Fill entire screen with color"""
        self.fill_rect(0, 0, self.width, self.height, color)

    def fill_rect(self, x, y, w, h, color):
        """Fill a rectangle with color"""
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        w = max(0, min(w, self.width - x))
        h = max(0, min(h, self.height - y))

        self.set_window(x, y, x + w - 1, y + h - 1)

        # Create color buffer
        color_bytes = struct.pack('>H', color)
        chunk_size = 512
        chunk = color_bytes * (chunk_size // 2)

        pixels = w * h
        for i in range(0, pixels, chunk_size // 2):
            remaining = min(chunk_size // 2, pixels - i)
            self._write_data(chunk[:remaining * 2])

    def rect(self, x, y, w, h, color):
        """Draw rectangle outline"""
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def hline(self, x, y, w, color):
        """Draw horizontal line"""
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        """Draw vertical line"""
        self.fill_rect(x, y, 1, h, color)

    def text(self, string, x, y, color, size=1):
        """Draw text on display (simple 8x8 font)"""
        for char in string:
            self._draw_char(char, x, y, color, size)
            x += 8 * size

    def _draw_char(self, char, x, y, color, size=1):
        """Draw a single character"""
        # Simple 8x8 font representation
        font = self._get_char_bitmap(char)

        for row in range(8):
            for col in range(8):
                if font[row] & (1 << (7 - col)):
                    if size == 1:
                        self.pixel(x + col, y + row, color)
                    else:
                        self.fill_rect(x + col * size, y +
                                       row * size, size, size, color)

    def _get_char_bitmap(self, char):
        """Get 8x8 bitmap for character (basic ASCII)"""
        # Basic font bitmaps for common characters
        fonts = {
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            'A': [0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x42],
            'B': [0x7C, 0x42, 0x42, 0x7C, 0x42, 0x42, 0x42, 0x7C],
            'C': [0x3C, 0x42, 0x40, 0x40, 0x40, 0x40, 0x42, 0x3C],
            'D': [0x78, 0x44, 0x42, 0x42, 0x42, 0x42, 0x44, 0x78],
            'E': [0x7E, 0x40, 0x40, 0x7C, 0x40, 0x40, 0x40, 0x7E],
            'F': [0x7E, 0x40, 0x40, 0x7C, 0x40, 0x40, 0x40, 0x40],
            'G': [0x3C, 0x42, 0x40, 0x40, 0x4E, 0x42, 0x42, 0x3C],
            'H': [0x42, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x42, 0x42],
            'I': [0x3E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x3E],
            'J': [0x02, 0x02, 0x02, 0x02, 0x02, 0x42, 0x42, 0x3C],
            'K': [0x44, 0x48, 0x50, 0x60, 0x50, 0x48, 0x44, 0x42],
            'L': [0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x7E],
            'M': [0x42, 0x66, 0x5A, 0x42, 0x42, 0x42, 0x42, 0x42],
            'N': [0x42, 0x62, 0x52, 0x4A, 0x46, 0x42, 0x42, 0x42],
            'O': [0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C],
            'P': [0x7C, 0x42, 0x42, 0x7C, 0x40, 0x40, 0x40, 0x40],
            'Q': [0x3C, 0x42, 0x42, 0x42, 0x42, 0x4A, 0x44, 0x3A],
            'R': [0x7C, 0x42, 0x42, 0x7C, 0x50, 0x48, 0x44, 0x42],
            'S': [0x3C, 0x42, 0x40, 0x3C, 0x02, 0x02, 0x42, 0x3C],
            'T': [0x7F, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08],
            'U': [0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C],
            'V': [0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x24, 0x18],
            'W': [0x42, 0x42, 0x42, 0x42, 0x5A, 0x66, 0x42, 0x42],
            'X': [0x42, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x42],
            'Y': [0x41, 0x22, 0x14, 0x08, 0x08, 0x08, 0x08, 0x08],
            'Z': [0x7E, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x7E],
            '0': [0x3C, 0x46, 0x4A, 0x52, 0x52, 0x52, 0x62, 0x3C],
            '1': [0x18, 0x28, 0x08, 0x08, 0x08, 0x08, 0x08, 0x3E],
            '2': [0x3C, 0x42, 0x02, 0x0C, 0x30, 0x40, 0x40, 0x7E],
            '3': [0x3C, 0x42, 0x02, 0x1C, 0x02, 0x02, 0x42, 0x3C],
            '4': [0x04, 0x0C, 0x14, 0x24, 0x44, 0x7E, 0x04, 0x04],
            '5': [0x7E, 0x40, 0x40, 0x7C, 0x02, 0x02, 0x42, 0x3C],
            '6': [0x3C, 0x42, 0x40, 0x7C, 0x42, 0x42, 0x42, 0x3C],
            '7': [0x7E, 0x02, 0x04, 0x08, 0x10, 0x10, 0x10, 0x10],
            '8': [0x3C, 0x42, 0x42, 0x3C, 0x42, 0x42, 0x42, 0x3C],
            '9': [0x3C, 0x42, 0x42, 0x3E, 0x02, 0x02, 0x42, 0x3C],
            ':': [0x00, 0x00, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00],
            '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18],
            '-': [0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00, 0x00],
            '+': [0x00, 0x08, 0x08, 0x3E, 0x08, 0x08, 0x00, 0x00],
            '!': [0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x08, 0x00],
            '/': [0x02, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x40],
        }

        # Return full block for unknown chars
        return fonts.get(char.upper(), [0xFF] * 8)

    def power_off(self):
        """Turn off display"""
        self._write_cmd(_DISPOFF)
        if self.backlight:
            self.backlight.off()

    def power_on(self):
        """Turn on display"""
        self._write_cmd(_DISPON)
        if self.backlight:
            self.backlight.on()
