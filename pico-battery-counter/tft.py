"""TFT Display module for ST7789 on Raspberry Pi"""
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import time
from config import (
    SPI_BUS, SPI_DEVICE, DC_PIN, RST_PIN, BL_PIN,
    DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_ROTATION
)


class ST7789:
    """
    ST7789 240x320 TFT display driver for Raspberry Pi.
    Uses SPI for communication.
    """

    # ST7789 Commands
    SWRESET = 0x01
    SLPOUT = 0x11
    NORON = 0x13
    INVOFF = 0x20
    INVON = 0x21
    DISPOFF = 0x28
    DISPON = 0x29
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    MADCTL = 0x36
    COLMOD = 0x3A

    def __init__(self, spi_bus=SPI_BUS, spi_device=SPI_DEVICE,
                 dc=DC_PIN, rst=RST_PIN, bl=BL_PIN,
                 width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT,
                 rotation=DISPLAY_ROTATION):
        """
        Initialize ST7789 display.

        Args:
            spi_bus: SPI bus number (0 or 1)
            spi_device: SPI device (CE0=0, CE1=1)
            dc: Data/Command GPIO pin (BCM)
            rst: Reset GPIO pin (BCM)
            bl: Backlight GPIO pin (BCM) - optional
            width: Display width in pixels
            height: Display height in pixels
            rotation: Display rotation (0, 90, 180, 270)
        """
        self.width = width
        self.height = height
        self.rotation = rotation

        # Setup GPIO pins
        GPIO.setmode(GPIO.BCM)
        self.dc_pin = dc
        self.rst_pin = rst
        self.bl_pin = bl

        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)

        if self.bl_pin is not None:
            GPIO.setup(self.bl_pin, GPIO.OUT)
            GPIO.output(self.bl_pin, GPIO.HIGH)  # Turn on backlight

        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 40000000  # 40MHz
        self.spi.mode = 0

        # Initialize display
        self.reset()
        self.init_display()

    def reset(self):
        """Hardware reset the display."""
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)

    def write_cmd(self, cmd):
        """Send command byte to display."""
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])

    def write_data(self, data):
        """Send data to display."""
        GPIO.output(self.dc_pin, GPIO.HIGH)
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)

    def init_display(self):
        """Initialize display with proper settings."""
        # Software reset
        self.write_cmd(self.SWRESET)
        time.sleep(0.15)

        # Sleep out
        self.write_cmd(self.SLPOUT)
        time.sleep(0.05)

        # Color mode: 16-bit color (RGB565)
        self.write_cmd(self.COLMOD)
        self.write_data(0x05)

        # Memory access control (rotation)
        self.write_cmd(self.MADCTL)
        if self.rotation == 0:  # Portrait
            self.write_data(0x00)
        elif self.rotation == 90:  # Landscape
            self.write_data(0x60)
        elif self.rotation == 180:  # Portrait inverted
            self.write_data(0xC0)
        elif self.rotation == 270:  # Landscape inverted
            self.write_data(0xA0)

        # Normal display mode
        self.write_cmd(self.NORON)
        time.sleep(0.01)

        # Display on
        self.write_cmd(self.DISPON)
        time.sleep(0.05)

    def set_window(self, x0, y0, x1, y1):
        """Set drawing window."""
        # Column address
        self.write_cmd(self.CASET)
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])

        # Row address
        self.write_cmd(self.RASET)
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

        # Write to RAM
        self.write_cmd(self.RAMWR)

    def display_image(self, image):
        """
        Display PIL Image on screen.

        Args:
            image: PIL Image object (RGB mode)
        """
        # Ensure image is correct size
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        # Convert to RGB565
        pixels = image.convert('RGB')
        pixel_data = []

        for y in range(self.height):
            for x in range(self.width):
                r, g, b = pixels.getpixel((x, y))
                # Convert RGB888 to RGB565
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                pixel_data.append(rgb565 >> 8)
                pixel_data.append(rgb565 & 0xFF)

        # Set window and write pixel data
        self.set_window(0, 0, self.width - 1, self.height - 1)

        # Write in chunks to avoid SPI buffer overflow
        chunk_size = 4096
        for i in range(0, len(pixel_data), chunk_size):
            chunk = pixel_data[i:i + chunk_size]
            self.write_data(chunk)

    def clear(self, color=(0, 0, 0)):
        """Clear screen to specified color."""
        image = Image.new('RGB', (self.width, self.height), color)
        self.display_image(image)

    def cleanup(self):
        """Clean up resources."""
        self.spi.close()
        GPIO.cleanup([self.dc_pin, self.rst_pin])
        if self.bl_pin is not None:
            GPIO.cleanup(self.bl_pin)


class TFT:
    """
    High-level TFT interface for battery counter display.
    Provides show() method compatible with original MicroPython interface.
    """

    def __init__(self):
        """Initialize TFT display with ST7789 driver."""
        self.display = ST7789()

        # Try to load a TrueType font, fall back to default if not available
        try:
            self.font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            self.font_medium = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            self.font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except IOError:
            print("Warning: TrueType fonts not found, using default font")
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def show(self, total, soil, water):
        """
        Display battery statistics.

        Args:
            total: Total number of batteries collected
            soil: Soil saved in kg
            water: Water saved in liters
        """
        # Create image with black background
        image = Image.new('RGB', (self.display.width,
                          self.display.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Define colors
        white = (255, 255, 255)
        green = (0, 255, 0)
        blue = (0, 191, 255)
        yellow = (255, 255, 0)

        # Draw title
        title = "Battery Counter"
        draw.text((10, 10), title, fill=yellow, font=self.font_large)

        # Draw separator line
        draw.line([(10, 50), (230, 50)], fill=white, width=2)

        # Draw battery count
        batteries_text = f"Batteries: {int(total)}"
        draw.text((10, 70), batteries_text, fill=white, font=self.font_medium)

        # Draw soil saved
        soil_text = f"Soil saved:"
        soil_value = f"{soil:.2f} kg"
        draw.text((10, 130), soil_text, fill=green, font=self.font_medium)
        draw.text((10, 160), soil_value, fill=green, font=self.font_large)

        # Draw water saved
        water_text = f"Water saved:"
        water_value = f"{water:.1f} L"
        draw.text((10, 220), water_text, fill=blue, font=self.font_medium)
        draw.text((10, 250), water_value, fill=blue, font=self.font_large)

        # Display the image
        self.display.display_image(image)

    def cleanup(self):
        """Clean up display resources."""
        self.display.cleanup()
