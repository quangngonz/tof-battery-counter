#!/usr/bin/env python3
"""
ST7789 240x320 TFT Display - Hello World Example
Raspberry Pi 4 with SPI connection
"""

import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont

# Pin Configuration
SPI_BUS = 0
SPI_DEVICE = 0
SCK_PIN = 11   # Pin 23 - GPIO11 (SPI0 SCLK) → SCL (clock)
MOSI_PIN = 10  # Pin 19 - GPIO10 (SPI0 MOSI) → SDA (data)
DC_PIN = 9     # Pin 21 - GPIO9 (SPI0 MISO) → DC (data/command)
RST_PIN = 25   # Pin 22 - GPIO25 → RES (reset)
CS_PIN = 8     # Pin 24 - GPIO8 (SPI0 CE0) → CS (chip select)
BL_PIN = 7     # Any free GPIO → BL (backlight)

# Display Configuration
WIDTH = 240
HEIGHT = 320
ROTATION = 0  # 0, 90, 180, or 270


class ST7789:
    """Driver for ST7789 TFT display"""

    def __init__(self, spi_bus=0, spi_device=0, dc_pin=9, rst_pin=25, bl_pin=7,
                 width=240, height=320, rotation=0):
        self.width = width
        self.height = height
        self.rotation = rotation

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.bl_pin = bl_pin

        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.bl_pin, GPIO.OUT)

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
        GPIO.output(self.bl_pin, GPIO.HIGH)

        # Initialization sequence
        self._send_command(0x01)  # Software reset
        time.sleep(0.15)

        self._send_command(0x11)  # Sleep out
        time.sleep(0.5)

        self._send_command(0x3A)  # Set color mode
        self._send_data(0x55)     # 16-bit color

        self._send_command(0x36)  # Memory data access control
        self._send_data(0x00)     # Default rotation

        self._send_command(0x2A)  # Column address set
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0xF0)     # 240

        self._send_command(0x2B)  # Row address set
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0x01)
        self._send_data(0x40)     # 320

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

        # Convert RGB888 to RGB565
        buffer = []
        for r, g, b in pixels:
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            buffer.append((rgb565 >> 8) & 0xFF)
            buffer.append(rgb565 & 0xFF)

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
        GPIO.output(self.bl_pin, GPIO.LOW)
        self.spi.close()
        GPIO.cleanup()


def main():
    """Main function to display Hello World"""
    print("Initializing ST7789 display...")

    # Create display instance
    display = ST7789(
        spi_bus=SPI_BUS,
        spi_device=SPI_DEVICE,
        dc_pin=DC_PIN,
        rst_pin=RST_PIN,
        bl_pin=BL_PIN,
        width=WIDTH,
        height=HEIGHT,
        rotation=ROTATION
    )

    try:
        # Clear display with black
        print("Clearing display...")
        display.clear((0, 0, 0))
        time.sleep(0.5)

        # Create image with text
        print("Drawing Hello World...")
        image = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Try to use a better font, fall back to default if not available
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Draw text
        text = "Hello World!"

        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (WIDTH - text_width) // 2
        y = (HEIGHT - text_height) // 2

        # Draw text with white color
        draw.text((x, y), text, font=font, fill=(255, 255, 255))

        # Display the image
        print("Displaying on screen...")
        display.display_image(image)

        print("Hello World displayed! Press Ctrl+C to exit.")

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        display.cleanup()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
