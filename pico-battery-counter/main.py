"""
Raspberry Pi 4 Time Display on ST7789 TFT
Fetches current time from NTP server and displays on 240x320 TFT
"""

import time
import ntptime
from machine import Pin, SPI
from utils.st7789 import ST7789

# Time server configuration
TIMEZONE_OFFSET = 0  # Adjust for your timezone (hours from UTC)

# GPIO Pin Configuration for Raspberry Pi 4
# Display pinout: BL, CS, DC, RES, SDA, SCL, VCC, GND
# RPi 4 Header: Pin 19=GPIO10, Pin 21=GPIO9, Pin 22=GPIO25, Pin 23=GPIO11, Pin 24=GPIO8
SPI_BUS = 0
SCK_PIN = 11   # Pin 23 - GPIO11 (SPI0 SCLK) → SCL (clock)
MOSI_PIN = 10  # Pin 19 - GPIO10 (SPI0 MOSI) → SDA (data)
DC_PIN = 9     # Pin 21 - GPIO9 (SPI0 MISO) → DC (data/command)
RST_PIN = 25   # Pin 22 - GPIO25 → RES (reset)
CS_PIN = 8     # Pin 24 - GPIO8 (SPI0 CE0) → CS (chip select)
BL_PIN = 7     # Any free GPIO → BL (backlight)

# Display Configuration
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
ROTATION = 4  # Orientation for 240x320

# Color definitions (RGB565)
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0
GRAY = 0x8410


def get_time_from_server():
    """Fetch current time from NTP server"""
    try:
        print("Fetching time from NTP server...")
        ntptime.settime()

        # Get current time
        current_time = time.localtime()

        # Apply timezone offset
        timestamp = time.mktime(current_time) + (TIMEZONE_OFFSET * 3600)
        adjusted_time = time.localtime(timestamp)

        return adjusted_time
    except Exception as e:
        print(f"Error fetching time: {e}")
        return None


def format_time(t):
    """Format time tuple to readable string"""
    hour = t[3]
    minute = t[4]
    second = t[5]
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def format_date(t):
    """Format date tuple to readable string"""
    year = t[0]
    month = t[1]
    day = t[2]

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_name = months[month - 1] if 1 <= month <= 12 else "???"

    return f"{day:02d} {month_name} {year}"


def format_weekday(t):
    """Format weekday from time tuple"""
    weekday = t[6]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
    return days[weekday] if 0 <= weekday < 7 else "Unknown"


def init_display():
    """Initialize ST7789 TFT display"""
    print("Initializing display...")

    # Initialize SPI
    spi = SPI(SPI_BUS, baudrate=40000000, polarity=0, phase=0,
              sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))

    # Initialize control pins
    dc = Pin(DC_PIN, Pin.OUT)
    rst = Pin(RST_PIN, Pin.OUT)
    cs = Pin(CS_PIN, Pin.OUT)
    bl = Pin(BL_PIN, Pin.OUT) if BL_PIN else None

    # Create display instance
    display = ST7789(spi, DISPLAY_WIDTH, DISPLAY_HEIGHT,
                     rst, dc, cs, bl, rotation=ROTATION)

    print("Display initialized!")
    return display


def draw_time_display(display, time_data):
    """Draw time and date on the display"""
    # Clear screen
    display.fill(BLACK)

    if time_data is None:
        # Show error message
        display.text("Time Error", 60, 140, RED, 2)
        display.text("Check NTP", 60, 160, RED, 2)
        return

    # Format time components
    time_str = format_time(time_data)
    date_str = format_date(time_data)
    weekday_str = format_weekday(time_data)

    # Display layout for 240x320 (portrait mode with rotation 4)
    # Title
    display.text("CURRENT TIME", 50, 40, CYAN, 2)

    # Time (large)
    display.text(time_str, 40, 100, WHITE, 3)

    # Date
    display.text(date_str, 50, 160, YELLOW, 2)

    # Weekday
    display.text(weekday_str, 40, 200, GREEN, 2)

    # Status indicator
    display.fill_rect(110, 270, 20, 20, GREEN)
    display.text("LIVE", 85, 295, GREEN, 1)


def main():
    """Main program loop"""
    print("=" * 40)
    print("Raspberry Pi 4 Time Display")
    print("=" * 40)

    # Initialize display
    display = init_display()

    # Show startup message
    display.fill(BLACK)
    display.text("Starting...", 70, 140, WHITE, 2)
    time.sleep(1)

    # Sync time from NTP
    display.fill(BLACK)
    display.text("Syncing NTP", 60, 140, CYAN, 2)
    time.sleep(1)

    # Main loop - update time every second
    last_update = 0
    update_interval = 1  # Update display every 1 second
    ntp_sync_interval = 3600  # Sync with NTP every hour
    last_ntp_sync = 0

    time_data = None

    while True:
        try:
            current = time.time()

            # Sync with NTP server periodically
            if current - last_ntp_sync >= ntp_sync_interval or time_data is None:
                time_data = get_time_from_server()
                last_ntp_sync = current

            # Update display
            if current - last_update >= update_interval:
                # Get current local time
                time_data = time.localtime()

                # Draw to display
                draw_time_display(display, time_data)

                last_update = current

                # Print to console
                print(f"{format_time(time_data)} - {format_date(time_data)}")

            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopping...")
            display.fill(BLACK)
            display.text("Goodbye!", 80, 150, WHITE, 2)
            time.sleep(1)
            display.power_off()
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
