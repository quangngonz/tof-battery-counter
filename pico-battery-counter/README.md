# Battery Counter - Raspberry Pi Version

A battery detection and counting system for Raspberry Pi 4 and Raspberry Pi Zero 2 with ST7789 TFT display and cloud synchronization.

## Hardware Requirements

### Supported Platforms

- Raspberry Pi 4 (all models)
- Raspberry Pi Zero 2 W

### Components

- **IR Sensor**: For battery detection (connected to GPIO17 by default)
- **ST7789 Display**: 3.2-inch 240×320 TFT display
- **Status LED**: Visual indicator (connected to GPIO27 by default)

### Wiring Diagram

#### ST7789 Display Connections (SPI)

| Display Pin | RPi Pin | BCM GPIO | Description |
| ----------- | ------- | -------- | ----------- |
| VCC         | Pin 1   | 3.3V     | Power       |
| GND         | Pin 6   | GND      | Ground      |
| DIN (MOSI)  | Pin 19  | GPIO10   | SPI MOSI    |
| CLK (SCK)   | Pin 23  | GPIO11   | SPI Clock   |
| CS          | Pin 24  | GPIO8    | SPI CE0     |
| DC          | Pin 22  | GPIO25   | Data/Cmd    |
| RST         | Pin 18  | GPIO24   | Reset       |
| BL          | Pin 16  | GPIO23   | Backlight   |

#### IR Sensor Connections

| Sensor Pin | RPi Pin | BCM GPIO | Description |
| ---------- | ------- | -------- | ----------- |
| VCC        | Pin 2   | 5V       | Power       |
| GND        | Pin 6   | GND      | Ground      |
| OUT        | Pin 11  | GPIO17   | Signal      |

#### Status LED

| LED Pin | RPi Pin | BCM GPIO | Description |
| ------- | ------- | -------- | ----------- |
| Anode   | Pin 13  | GPIO27   | LED +       |
| Cathode | GND     | GND      | LED -       |

_Note: Use a current-limiting resistor (220Ω-330Ω) in series with the LED_

## Installation

### 1. System Setup

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-dev python3-pil git

# Enable SPI interface
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable
# Or use command line:
sudo raspi-config nonint do_spi 0

# Reboot to apply changes
sudo reboot
```

### 2. Clone or Copy Project Files

```bash
# Create project directory
mkdir -p ~/battery-counter
cd ~/battery-counter

# Copy all project files here:
# - main.py
# - sensor.py
# - sync.py
# - tft.py
# - config.py
# - requirements.txt
```

### 3. Install Python Dependencies

```bash
# Install required packages
pip3 install -r requirements.txt

# Verify installation
python3 -c "import RPi.GPIO, spidev, requests, PIL; print('All packages installed successfully')"
```

### 4. Configure the Application

Edit `config.py` to customize settings:

```python
# Device identification
DEVICE_ID = "rpi_zero_1"  # Change for each device

# GPIO pins (BCM numbering)
IR_PIN = 17      # IR sensor
LED_PIN = 27     # Status LED

# SPI and display pins
DC_PIN = 25      # Data/Command
RST_PIN = 24     # Reset
BL_PIN = 23      # Backlight

# Display settings
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
DISPLAY_ROTATION = 0  # 0=portrait, 90=landscape

# Cache file location
CACHE_FILE = "/var/local/battery_counter_cache.json"
```

### 5. Create Cache Directory

```bash
# Create cache directory with proper permissions
sudo mkdir -p /var/local
sudo chown $USER:$USER /var/local
```

## Running the Application

### Manual Execution

```bash
# Run directly
cd ~/battery-counter
python3 main.py
```

### Run on Boot (systemd service)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/battery-counter.service
```

Add the following content:

```ini
[Unit]
Description=Battery Counter Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/battery-counter
ExecStart=/usr/bin/python3 /home/pi/battery-counter/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable battery-counter.service

# Start the service
sudo systemctl start battery-counter.service

# Check status
sudo systemctl status battery-counter.service

# View logs
sudo journalctl -u battery-counter.service -f
```

### Control the Service

```bash
# Start service
sudo systemctl start battery-counter.service

# Stop service
sudo systemctl stop battery-counter.service

# Restart service
sudo systemctl restart battery-counter.service

# Disable auto-start
sudo systemctl disable battery-counter.service
```

## Usage

Once running, the system will:

1. **Monitor IR Sensor**: Continuously checks for battery detection with debounce protection
2. **Cache Records Locally**: Stores detections locally if network is unavailable
3. **Sync to Cloud**: Automatically uploads cached records to the API server
4. **Fetch Statistics**: Periodically retrieves total counts from the server
5. **Update Display**: Shows real-time statistics including:
   - Total batteries collected
   - Soil saved (kg)
   - Water saved (liters)

### LED Indicator

- **Blinking**: Normal operation (blinks during each loop iteration)
- **Off**: Application not running

## Troubleshooting

### Display Not Working

```bash
# Check SPI is enabled
lsmod | grep spi_
# Should show: spi_bcm2835

# Test SPI devices exist
ls -l /dev/spidev*
# Should show: /dev/spidev0.0

# Check connections
# Verify all display pins are properly connected
```

### GPIO Permission Errors

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Log out and back in for changes to take effect
```

### Network/API Errors

```bash
# Check internet connectivity
ping -c 3 asep-battery-counter-api.vercel.app

# Verify DNS resolution
nslookup asep-battery-counter-api.vercel.app

# Check cache file
cat /var/local/battery_counter_cache.json
```

### View Logs

```bash
# If running manually
python3 main.py

# If running as service
sudo journalctl -u battery-counter.service -f

# View last 100 lines
sudo journalctl -u battery-counter.service -n 100
```

### Test Individual Components

```python
# Test IR sensor
python3 -c "from sensor import IRSensor; import time; s = IRSensor(17); [print('Triggered!') if s.check() else None or time.sleep(0.1) for _ in range(100)]"

# Test API connection
python3 -c "from sync import fetch_stats; print(fetch_stats())"

# Test display
python3 -c "from tft import TFT; t = TFT(); t.show(42, 0.84, 6.3); import time; time.sleep(5); t.cleanup()"
```

## File Descriptions

- **`main.py`**: Main application loop and initialization
- **`sensor.py`**: IR sensor interface with debouncing
- **`sync.py`**: Cloud synchronization and caching logic
- **`tft.py`**: ST7789 display driver and rendering
- **`config.py`**: Configuration settings and pin mappings
- **`requirements.txt`**: Python package dependencies

## API Endpoints

The application communicates with the following endpoints:

- **POST** `https://asep-battery-counter-api.vercel.app/log`

  - Logs battery detection events
  - Body: `{"timestamp": <unix_timestamp>, "amount": 1, "device_id": "<device_id>"}`

- **GET** `https://asep-battery-counter-api.vercel.app/stats`
  - Retrieves aggregate statistics
  - Returns: `{"total": <count>, "soil": <kg>, "water": <liters>}`

## Architecture

### Hardware Abstraction Layer

- **GPIO**: Uses `RPi.GPIO` library for pin control
- **SPI**: Uses `spidev` for display communication
- **Display**: Custom ST7789 driver with PIL for graphics

### Key Features Preserved

- ✅ Debounced IR sensor detection (150ms)
- ✅ Local caching of unsynced records
- ✅ Periodic server statistics fetching
- ✅ Exact API endpoint compatibility
- ✅ Same calculation logic (soil: 0.02kg, water: 0.15L per battery)

### Differences from MicroPython Version

- Network connectivity assumed (no WiFi management)
- Uses standard Python file I/O
- Implements complete ST7789 driver
- Enhanced error handling and logging
- Systemd service integration
- Signal handling for clean shutdown

## Performance

- **Loop frequency**: ~20Hz (50ms delay)
- **Stats fetch interval**: Every 100 loops (~5 seconds)
- **Display refresh**: Every loop iteration
- **SPI speed**: 40MHz for fast display updates

## License

This project is part of the ASEP Battery Counter initiative.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review system logs: `sudo journalctl -u battery-counter.service -f`
3. Verify hardware connections
4. Test components individually
