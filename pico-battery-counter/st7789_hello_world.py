#!/usr/bin/env python3
"""
ST7789 240x320 TFT Display - Hello World Example
Raspberry Pi 4 with SPI connection
"""

import time
from PIL import Image, ImageDraw, ImageFont
from utils.st7789_display import ST7789

# Pin Configuration
SPI_BUS = 0
SPI_DEVICE = 0
DC_PIN = 9     # Pin 21 - GPIO9 (SPI0 MISO) → DC (data/command)
RST_PIN = 25   # Pin 22 - GPIO25 → RES (reset)
CS_PIN = 8     # Pin 24 - GPIO8 (SPI0 CE0) → CS (chip select)
BL_PIN = None  # Set to None to disable, or use GPIO like 18, 23, 24, etc.

# Display Configuration
WIDTH = 240
HEIGHT = 320
ROTATION = 270  # 0, 90, 180, or 270


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
        image = Image.new('RGB', (display.width, display.height), (0, 0, 0))
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

        x = (display.width - text_width) // 2
        y = (display.height - text_height) // 2

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
