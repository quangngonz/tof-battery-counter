"""
ST7789 TFT Display Driver for Raspberry Pi
High-level driver for ST7789 240x320 SPI displays

This driver provides a simple interface for:
- Display initialization and configuration
- Drawing primitives (pixels, rectangles, text)
- Color management (RGB565)
- Screen rotation and orientation
"""

import time


# ST7789 Command Set
CMD_NOP = 0x00
CMD_SWRESET = 0x01
CMD_SLPOUT = 0x11
CMD_NORON = 0x13
CMD_INVOFF = 0x20
CMD_INVON = 0x21
CMD_DISPOFF = 0x28
CMD_DISPON = 0x29
CMD_CASET = 0x2A
CMD_RASET = 0x2B
CMD_RAMWR = 0x2C
CMD_MADCTL = 0x36
CMD_COLMOD = 0x3A


# MADCTL (Memory Data Access Control) bits
MADCTL_MY = 0x80   # Row address order
MADCTL_MX = 0x40   # Column address order
MADCTL_MV = 0x20   # Row/Column exchange
MADCTL_ML = 0x10   # Vertical refresh order
MADCTL_RGB = 0x00  # RGB order
MADCTL_BGR = 0x08  # BGR order
MADCTL_MH = 0x04   # Horizontal refresh order


# Rotation configurations (MADCTL values)
ROTATIONS = {
    0: MADCTL_MX | MADCTL_MY | MADCTL_RGB,                    # 0 degrees
    1: MADCTL_MY | MADCTL_MV | MADCTL_RGB,                    # 90 degrees
    2: MADCTL_RGB,                                             # 180 degrees
    3: MADCTL_MX | MADCTL_MV | MADCTL_RGB,                    # 270 degrees
    # Portrait (240x320)
    4: MADCTL_MX | MADCTL_BGR,
}


class ST7789:
    """
    ST7789 TFT Display Driver

    Supports SPI communication with hardware control pins.
    Optimized for 240x320 displays on Raspberry Pi.
    """

    def __init__(self, spi, width, height, rst, dc, cs=None, bl=None, rotation=0):
        """
        Initialize ST7789 display

        Args:
            spi: SpiDev instance for SPI communication
            width: Display width in pixels
            height: Display height in pixels
            rst: Reset pin (gpiozero OutputDevice)
            dc: Data/Command pin (gpiozero OutputDevice)
            cs: Chip Select pin (optional, can be None if hardware controlled)
            bl: Backlight pin (optional, gpiozero OutputDevice)
            rotation: Display rotation (0, 1, 2, 3, or 4)
        """
        self.spi = spi
        self.width = width
        self.height = height
        self.rst = rst
        self.dc = dc
        self.cs = cs
        self.bl = bl
        self.rotation = rotation

        # Initialize display
        self._reset()
        self._init_display()
        self._set_rotation(rotation)

        # Turn on backlight if available
        if self.bl:
            self.bl.on()

    def _reset(self):
        """Hardware reset the display"""
        if self.rst:
            self.rst.on()
            time.sleep(0.01)
            self.rst.off()
            time.sleep(0.01)
            self.rst.on()
            time.sleep(0.12)

    def _write_command(self, cmd):
        """Write command byte to display"""
        self.dc.off()  # Command mode
        self.spi.writebytes([cmd])

    def _write_data(self, data):
        """Write data byte(s) to display"""
        self.dc.on()  # Data mode
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)

    def _init_display(self):
        """Initialize display with configuration sequence"""
        # Software reset
        self._write_command(CMD_SWRESET)
        time.sleep(0.15)

        # Sleep out
        self._write_command(CMD_SLPOUT)
        time.sleep(0.5)

        # Color mode: 16-bit (RGB565)
        self._write_command(CMD_COLMOD)
        self._write_data(0x55)
        time.sleep(0.01)

        # Normal display mode
        self._write_command(CMD_NORON)
        time.sleep(0.01)

        # Display on
        self._write_command(CMD_DISPON)
        time.sleep(0.1)

    def _set_rotation(self, rotation):
        """Set display rotation"""
        self.rotation = rotation
        madctl = ROTATIONS.get(rotation, ROTATIONS[0])

        self._write_command(CMD_MADCTL)
        self._write_data(madctl)

    def _set_window(self, x0, y0, x1, y1):
        """Set the active drawing window"""
        # Column address set
        self._write_command(CMD_CASET)
        self._write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])

        # Row address set
        self._write_command(CMD_RASET)
        self._write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

        # Write to RAM
        self._write_command(CMD_RAMWR)

    def fill(self, color):
        """Fill entire screen with a color"""
        self._set_window(0, 0, self.width - 1, self.height - 1)

        # Create color data (RGB565 format, 2 bytes per pixel)
        hi = color >> 8
        lo = color & 0xFF

        # Send color data for all pixels
        pixel_data = bytes([hi, lo] * 4096)  # Chunk size
        pixels_remaining = self.width * self.height

        self.dc.on()
        while pixels_remaining > 0:
            chunk_size = min(4096, pixels_remaining)
            self.spi.writebytes(pixel_data[:chunk_size * 2])
            pixels_remaining -= chunk_size

    def pixel(self, x, y, color):
        """Draw a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._set_window(x, y, x, y)
            self.dc.on()
            self.spi.writebytes([color >> 8, color & 0xFF])

    def fill_rect(self, x, y, width, height, color):
        """Draw a filled rectangle"""
        x1 = x + width - 1
        y1 = y + height - 1

        # Clip to screen bounds
        if x1 >= self.width:
            x1 = self.width - 1
        if y1 >= self.height:
            y1 = self.height - 1
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return

        self._set_window(x, y, x1, y1)

        # Create color data
        hi = color >> 8
        lo = color & 0xFF
        pixel_count = (x1 - x + 1) * (y1 - y + 1)

        # Send color data
        chunk_size = 4096
        pixel_data = bytes([hi, lo] * chunk_size)

        self.dc.on()
        while pixel_count > 0:
            chunk = min(chunk_size, pixel_count)
            self.spi.writebytes(pixel_data[:chunk * 2])
            pixel_count -= chunk

    def text(self, text, x, y, color, size=1):
        """
        Draw text on display using a simple 5x7 bitmap font

        Args:
            text: String to display
            x: X coordinate (top-left)
            y: Y coordinate (top-left)
            color: Text color (RGB565)
            size: Font scale multiplier (1, 2, 3, etc.)
        """
        # Simple 5x7 bitmap font (ASCII 32-126)
        # For simplicity, using a basic character set
        cursor_x = x

        for char in text:
            if char == ' ':
                cursor_x += 6 * size
                continue

            # Draw a simple block for each character (placeholder)
            # In a full implementation, you'd use a proper bitmap font
            self._draw_char(char, cursor_x, y, color, size)
            cursor_x += 6 * size

    def _draw_char(self, char, x, y, color, size):
        """Draw a single character (simplified placeholder)"""
        # This is a simplified placeholder that draws filled rectangles
        # A full implementation would use a proper bitmap font

        # Simple font patterns (5x7 pixels) for common characters
        font = self._get_char_bitmap(char)

        if font:
            for row in range(7):
                for col in range(5):
                    if font[row] & (1 << (4 - col)):
                        if size == 1:
                            self.pixel(x + col, y + row, color)
                        else:
                            self.fill_rect(x + col * size, y +
                                           row * size, size, size, color)

    def _get_char_bitmap(self, char):
        """Get bitmap pattern for a character (simplified font)"""
        # Simplified 5x7 font bitmaps for common characters
        # Each row is a 5-bit pattern (bits 4-0 represent columns 0-4)
        font_data = {
            '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
            '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
            '2': [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
            '3': [0x0E, 0x11, 0x01, 0x0E, 0x01, 0x11, 0x0E],
            '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
            '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
            '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
            '7': [0x1F, 0x01, 0x02, 0x04, 0x04, 0x04, 0x04],
            '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
            '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
            ':': [0x00, 0x00, 0x04, 0x00, 0x04, 0x00, 0x00],
            'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
            'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
            'C': [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
            'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
            'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
            'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
            'G': [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
            'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
            'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
            'J': [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
            'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
            'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
            'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
            'N': [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
            'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
            'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
            'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
            'S': [0x0E, 0x11, 0x10, 0x0E, 0x01, 0x11, 0x0E],
            'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
            'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
            'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
            'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
            'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
            'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
            'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        }

        return font_data.get(char.upper(), [0x00] * 7)

    def power_off(self):
        """Turn off display"""
        self._write_command(CMD_DISPOFF)
        if self.bl:
            self.bl.off()

    def power_on(self):
        """Turn on display"""
        self._write_command(CMD_DISPON)
        if self.bl:
            self.bl.on()

    def invert(self, invert=True):
        """Invert display colors"""
        if invert:
            self._write_command(CMD_INVON)
        else:
            self._write_command(CMD_INVOFF)


def rgb_to_565(r, g, b):
    """
    Convert RGB888 (24-bit) to RGB565 (16-bit)

    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)

    Returns:
        16-bit RGB565 color value
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def color565(r, g, b):
    """Alias for rgb_to_565"""
    return rgb_to_565(r, g, b)
