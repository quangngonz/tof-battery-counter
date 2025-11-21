#!/usr/bin/env python3
"""
ST7789 240x320 TFT Display - Live Clock
Displays current date and time, updating every second
Rotated 90 degrees to the left (landscape mode)
"""

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from utils.st7789_display import ST7789
import os
from pathlib import Path

# Add parent directory to Python path to allow imports from utils


# Pin Configuration
SPI_BUS = 0
SPI_DEVICE = 0
DC_PIN = 9     # Pin 21 - GPIO9 (SPI0 MISO) → DC (data/command)
RST_PIN = 25   # Pin 22 - GPIO25 → RES (reset)
CS_PIN = 8     # Pin 24 - GPIO8 (SPI0 CE0) → CS (chip select)
BL_PIN = None  # Set to GPIO number if backlight control is needed

# Display Configuration
WIDTH = 240
HEIGHT = 320

ROTATIONS = [0, 90, 180, 270]
ROTATION = ROTATIONS[3]  # Rotate 90 degrees to the left (landscape)


def draw_clock(width, height):
    """
    Create an image with current date and time

    Args:
        width: Image width
        height: Image height

    Returns:
        PIL Image with clock display
    """
    # Create black background
    image = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Get current date and time
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%A, %B %d, %Y")

    # Load fonts
    try:
        time_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        date_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        # Fallback to default font
        time_font = ImageFont.load_default()
        date_font = ImageFont.load_default()

    # Calculate text positions for centering
    time_bbox = draw.textbbox((0, 0), time_str, font=time_font)
    time_width = time_bbox[2] - time_bbox[0]
    time_height = time_bbox[3] - time_bbox[1]

    date_bbox = draw.textbbox((0, 0), date_str, font=date_font)
    date_width = date_bbox[2] - date_bbox[0]
    date_height = date_bbox[3] - date_bbox[1]

    # Position time in upper-center area
    time_x = (width - time_width) // 2
    time_y = (height // 2) - time_height - 20

    # Position date in lower-center area
    date_x = (width - date_width) // 2
    date_y = (height // 2) + 20

    # Draw time and date
    draw.text((time_x, time_y), time_str, font=time_font, fill=(255, 255, 255))
    draw.text((date_x, date_y), date_str, font=date_font, fill=(180, 180, 180))

    return image


def main():
    """Main function to display live clock"""
    print("Initializing ST7789 display...")

    # Create display instance with 90-degree rotation
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

        print("Starting clock display... Press Ctrl+C to exit.")

        # Update clock every second
        while True:
            # Draw clock image
            clock_image = draw_clock(display.width, display.height)

            # Display on screen
            display.display_image(clock_image)

            # Wait until next second
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        display.cleanup()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
