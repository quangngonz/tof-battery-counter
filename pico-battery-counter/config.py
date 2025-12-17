"""
Configuration constants for the IR sensor battery counter
"""

# API Endpoints
API_LOG = "https://asep-battery-counter-api.vercel.app/log"
API_STATS = "https://asep-battery-counter-api.vercel.app/stats"

# GPIO Configuration (BCM numbering)
IR_PIN = 15
LED_PIN = 14

# Limit switch GPIO
LIMIT_SWITCH_PIN = 17

# Device Configuration
DEVICE_ID = "rpi4_1"

# File Paths
CACHE_FILE = "cache.json"

# Network Configuration
WIFI_CHECK_HOST = "8.8.8.8"

# Timing Configuration
DEBOUNCE_MS = 100
SYNC_INTERVAL_SECONDS = 5
STATS_UPDATE_INTERVAL_LOOPS = 100
MAIN_LOOP_SLEEP = 0.05

# ToF Sensor Configuration
TOF_I2C_BUS = 1
TOF_ADDRESS = 0x29
TOF_XSHUT_PIN = 17
TOF_THRESHOLD_MM = 15

# Display Configuration
SHOW_DISTANCE_MEASUREMENT = False
