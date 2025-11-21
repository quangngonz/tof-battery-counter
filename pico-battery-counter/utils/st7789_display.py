#!/usr/bin/env python3
"""
ST7789 TFT Display Driver
Supports 240x320 displays with SPI interface
Raspberry Pi 4 compatible
"""

import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image


class ST7789:
    """Driver for ST7789 TFT display"""

    def __init__(self, spi_bus=0, spi_device=0, dc_pin=9, rst_pin=25, bl_pin=None,
                 width=240, height=320, rotation=0):
        """
        Initialize ST7789 display

        Args:
            spi_bus: SPI bus number (0 or 1)
            spi_device: SPI device number (0 or 1)
            dc_pin: GPIO pin for Data/Command signal
            rst_pin: GPIO pin for Reset signal
            bl_pin: GPIO pin for Backlight control (None to disable)
            width: Display width in pixels
            height: Display height in pixels
            rotation: Display rotation in degrees (0, 90, 180, 270)
        """
        self.base_width = width
        self.base_height = height
        self.rotation = rotation

        # Adjust width/height based on rotation
        if rotation in (90, 270):
            self.width = height
            self.height = width
        else:
            self.width = width
            self.height = height

        # Setup GPIO pins (assumes GPIO.setmode() already called)
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.bl_pin = bl_pin

        # Setup pins with error handling
        try:
            GPIO.setup(self.dc_pin, GPIO.OUT)
            GPIO.setup(self.rst_pin, GPIO.OUT)
            if bl_pin is not None:
                GPIO.setup(self.bl_pin, GPIO.OUT)
        except Exception as e:
            print(f"GPIO setup error: {e}")
            print("Trying to continue anyway...")

        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 40000000  # 40 MHz
        self.spi.mode = 0

        # Initialize display
        self._init_display()

    def _init_display(self):
        """Initialize the ST7789 display"""
        self._reset()

        # Turn on backlight
        try:
            if self.bl_pin is not None:
                GPIO.output(self.bl_pin, GPIO.HIGH)
        except Exception as e:
            print(f"Backlight control error: {e}")

        # Initialization sequence
        self._send_command(0x01)  # Software reset
        time.sleep(0.15)

        self._send_command(0x11)  # Sleep out
        time.sleep(0.5)

        self._send_command(0x3A)  # Set color mode
        self._send_data(0x55)     # 16-bit color

        # Memory data access control - set rotation and BGR bit
        self._send_command(0x36)
        rotation_values = {
            0: 0x00,    # Normal
            90: 0x60,   # Rotate 90 degrees (landscape)
            180: 0xC0,  # Rotate 180 degrees
            270: 0xA0   # Rotate 270 degrees
        }
        # Set bit 3 (0x08) to enable BGR color order
        self._send_data(rotation_values.get(self.rotation, 0x00) | 0x08)

        self._send_command(0x2A)  # Column address set
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data((self.base_width - 1) >> 8)
        self._send_data((self.base_width - 1) & 0xFF)

        self._send_command(0x2B)  # Row address set
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data((self.base_height - 1) >> 8)
        self._send_data((self.base_height - 1) & 0xFF)

        self._send_command(0x21)  # Inversion on

        self._send_command(0x13)  # Normal display on

        self._send_command(0x29)  # Display on
        time.sleep(0.1)

    def _reset(self):
        """Hardware reset"""
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)

    def _send_command(self, command):
        """Send command to display"""
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([command])

    def _send_data(self, data):
        """Send data to display"""
        GPIO.output(self.dc_pin, GPIO.HIGH)
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)

    def display_image(self, image):
        """Display a PIL Image on the screen"""
        # Resize image if needed
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        # Convert to RGB565
        rgb_image = image.convert('RGB')
        pixels = list(rgb_image.getdata())

        # Convert RGB888 to BGR565 (ST7789 uses BGR byte order)
        buffer = []
        for r, g, b in pixels:
            # Swap R and B for BGR format
            bgr565 = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
            buffer.append((bgr565 >> 8) & 0xFF)
            buffer.append(bgr565 & 0xFF)

        # Set drawing window
        self._send_command(0x2A)  # Column address set
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data((self.width - 1) >> 8)
        self._send_data((self.width - 1) & 0xFF)

        self._send_command(0x2B)  # Row address set
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data((self.height - 1) >> 8)
        self._send_data((self.height - 1) & 0xFF)

        self._send_command(0x2C)  # Memory write

        # Send image data in chunks
        chunk_size = 4096
        for i in range(0, len(buffer), chunk_size):
            self._send_data(buffer[i:i + chunk_size])

    def clear(self, color=(0, 0, 0)):
        """Clear display with specified color"""
        image = Image.new('RGB', (self.width, self.height), color)
        self.display_image(image)

    def cleanup(self):
        """Cleanup GPIO and SPI"""
        try:
            if self.bl_pin is not None:
                GPIO.output(self.bl_pin, GPIO.LOW)
        except:
            pass
        self.spi.close()
        GPIO.cleanup()


class TFT:
    """
    High-level TFT display wrapper for battery counter statistics
    """

    def __init__(self):
        """
        Initialize the TFT display with default settings
        """
        try:
            # Initialize ST7789 display with common settings
            # Adjust these parameters based on your specific display
            self.display = ST7789(
                spi_bus=0,
                spi_device=0,
                dc_pin=9,
                rst_pin=25,
                bl_pin=13,
                width=240,
                height=320,
                rotation=270  # Landscape mode
            )
            self.display.clear((0, 0, 0))  # Clear to black
            print("TFT Display initialized")
        except Exception as e:
            print(f"Failed to initialize TFT display: {e}")
            self.display = None

    def show(self, total, soil, water):
        """
        Display battery counter statistics on the TFT

        Args:
            total: Total battery count
            soil: Estimated soil pollution (kg)
            water: Estimated water pollution (L)
        """
        if self.display is None:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont

            # Create image
            img = Image.new('RGB', (self.display.width,
                            self.display.height), (0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Try to use a default font, fallback to basic if not available
            try:
                font_large = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
                font_medium = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                font_small = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Draw title
            draw.text((10, 10), "Battery Counter", fill=(
                255, 255, 255), font=font_medium)

            # Draw separator line
            draw.line([(10, 45), (310, 45)], fill=(100, 100, 100), width=2)

            # Draw total count
            draw.text((10, 60), "Total Batteries:", fill=(
                100, 200, 255), font=font_medium)
            draw.text((10, 90), f"{int(total)}", fill=(
                255, 255, 255), font=font_large)

            # Draw vertical battery icon aligned to the right
            battery_x = 278
            battery_y = 60
            battery_width = 30
            battery_height = 60

            # Battery terminal (positive) at top - GREEN
            terminal_width = 14
            terminal_height = 5
            draw.rectangle(
                [(battery_x + (battery_width - terminal_width) // 2, battery_y - terminal_height),
                 (battery_x + (battery_width + terminal_width) // 2, battery_y)],
                fill=(0, 200, 0)
            )

            # Battery body with dark green outline - GREEN
            draw.rectangle(
                [(battery_x, battery_y), (battery_x +
                                          battery_width, battery_y + battery_height)],
                outline=(0, 200, 0), fill=None, width=3
            )

            # Battery fill (lighter green inside) - GREEN
            fill_height = int(battery_height * 0.75)
            draw.rectangle(
                [(battery_x + 3, battery_y + battery_height - fill_height - 3),
                 (battery_x + battery_width - 3, battery_y + battery_height - 3)],
                fill=(50, 255, 50)
            )

            # Draw separator
            draw.line([(10, 140), (310, 140)], fill=(100, 100, 100), width=1)

            # Draw soil pollution
            draw.text((10, 155), "Soil Impact:", fill=(
                100, 150, 255), font=font_small)
            draw.text((10, 180), f"{soil:.2f} kg", fill=(
                150, 200, 255), font=font_medium)

            # Draw water pollution
            draw.text((160, 155), "Water Impact:", fill=(
                255, 150, 100), font=font_small)
            draw.text((160, 180), f"{water:.2f} L", fill=(
                255, 200, 150), font=font_medium)

            # Display the image
            self.display.display_image(img)

        except Exception as e:
            print(f"Error updating display: {e}")

    def cleanup(self):
        """
        Clean up display resources
        """
        if self.display is not None:
            try:
                self.display.cleanup()
            except Exception as e:
                print(f"Error cleaning up display: {e}")
