# Configuration for Raspberry Pi Battery Counter
# Network configuration is handled by Raspberry Pi OS

# API Endpoints
API_LOG = "https://asep-battery-counter-api.vercel.app/log"
API_STATS = "https://asep-battery-counter-api.vercel.app/stats"

# GPIO Pin Configuration (BCM numbering)
IR_PIN = 17      # GPIO17 (Physical pin 11) - IR sensor input
LED_PIN = 27     # GPIO27 (Physical pin 13) - Status LED

# SPI Configuration for ST7789 Display
SPI_BUS = 0           # SPI0
SPI_DEVICE = 0        # CE0
DC_PIN = 25           # GPIO25 (Physical pin 22) - Data/Command
RST_PIN = 24          # GPIO24 (Physical pin 18) - Reset
BL_PIN = 23           # GPIO23 (Physical pin 16) - Backlight (optional)

# Display Configuration
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
DISPLAY_ROTATION = 0  # 0=portrait, 90=landscape, etc.

# Device Configuration
DEVICE_ID = "rpi_zero_1"  # Change this for each device

# Sync Configuration
CACHE_FILE = "/var/local/battery_counter_cache.json"
