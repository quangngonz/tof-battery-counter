# Battery Counter - Raspberry Pi 4

A Raspberry Pi 4 application that counts IR beam breaks (battery detections), caches events locally, syncs them to a cloud API, and displays real-time statistics on a TFT display.

## Features

- **Non-blocking IR Sensor Detection**: Hardware-debounced beam break counting
- **Local Caching**: Unsent events stored in JSON for reliability
- **Background Sync**: Asynchronous cloud synchronization via threading
- **TFT Display**: Real-time statistics visualization (ST7789)
- **LED Indicator**: Visual feedback for system activity

## Hardware Requirements

- Raspberry Pi 4 (running full Linux)
- IR Break Beam Sensor (connected to GPIO 15)
- LED (connected to GPIO 14)
- ST7789 TFT Display (240x320, SPI)
  - DC: GPIO 9
  - RST: GPIO 25
  - BL: GPIO 13
  - SPI: Bus 0, Device 0

## Project Structure

```
project/
├── main.py                 # Main application loop
├── config.py              # Configuration constants
├── requirements.txt       # Python dependencies
├── cache.json            # Local event cache (auto-generated)
├── utils/
│   ├── __init__.py
│   ├── sensor.py         # IR sensor with debouncing
│   ├── sync.py           # Cache management & API sync
│   └── st7789_display.py # TFT display driver & wrapper
└── draft/                # Development examples
```

## Installation

### 1. System Setup

Ensure your Raspberry Pi 4 is running a recent version of Raspberry Pi OS:

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Enable SPI

```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
```

Reboot after enabling SPI:

```bash
sudo reboot
```

### 3. Install Python Dependencies

```bash
cd /path/to/pico-battery-counter
pip3 install -r requirements.txt
```

Or install system-wide:

```bash
sudo pip3 install -r requirements.txt
```

## Configuration

Edit `config.py` to customize:

```python
# API Endpoints
API_LOG = "https://asep-battery-counter-api.vercel.app/log"
API_STATS = "https://asep-battery-counter-api.vercel.app/stats"

# GPIO Pins (BCM numbering)
IR_PIN = 15
LED_PIN = 14

# Device Identifier
DEVICE_ID = "rpi4_1"

# Timing
DEBOUNCE_MS = 150
SYNC_INTERVAL_SECONDS = 5
STATS_UPDATE_INTERVAL_LOOPS = 100
```

## Usage

### Run the Application

```bash
python3 main.py
```

### Run on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/battery-counter.service
```

Add:

```ini
[Unit]
Description=Battery Counter Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pico-battery-counter
ExecStart=/usr/bin/python3 /home/pi/pico-battery-counter/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable battery-counter.service
sudo systemctl start battery-counter.service
sudo systemctl status battery-counter.service
```

## How to Set Up and Run the Service

To set up and run the battery-counter service on your Raspberry Pi, follow these steps:

1. Make the setup script executable:

   ```bash
   chmod +x setup_service.sh
   ```

2. Run the setup script:
   ```bash
   ./setup_service.sh
   ```

This will copy the service file to the appropriate location, reload the systemd daemon, enable the service to run on startup, and start the service immediately.

## How It Works

### Main Loop (`main.py`)

1. Initializes IR sensor, LED, and TFT display
2. Starts background sync thread
3. Continuously monitors IR sensor (non-blocking)
4. On detection:
   - Adds record to local cache
   - Provides LED feedback
5. Every 100 loops:
   - Fetches latest stats from API
   - Calculates display values (API + unsynced)
   - Updates TFT display

### IR Sensor (`utils/sensor.py`)

- Uses `RPi.GPIO` in BCM mode
- Software debouncing with `time.monotonic()`
- Detects falling edge (HIGH → LOW)
- Returns `True` only once per event

### Sync Module (`utils/sync.py`)

**Cache Management:**

- `load_cache()`: Load cached events from JSON
- `save_cache()`: Save events to JSON
- `add_record()`: Append new detection event

**Networking:**

- `has_internet()`: Quick ping test to 8.8.8.8
- `fetch_stats()`: GET request to stats API

**Background Thread:**

- Runs every 5 seconds
- Checks internet connectivity
- POSTs cached records to API
- Removes successfully synced records
- Continues even if main loop blocks

### Display (`utils/st7789_display.py`)

- `ST7789`: Low-level SPI driver
- `TFT`: High-level wrapper with `show()` method
- Displays:
  - Total battery count
  - Soil impact (kg)
  - Water impact (L)

## API Integration

### POST /log

Submit a battery detection event:

```json
{
  "timestamp": 1700000000,
  "amount": 1,
  "device": "rpi4_1"
}
```

**Response:** `200 OK` on success

### GET /stats

Retrieve cumulative statistics:

```json
{
  "total": 1234,
  "soil": 24.68,
  "water": 185.1
}
```

## Troubleshooting

### GPIO Permissions

If you get permission errors:

```bash
sudo usermod -a -G gpio,spi $USER
# Log out and back in
```

### Display Not Working

Check SPI is enabled:

```bash
lsmod | grep spi
# Should show: spi_bcm2835
```

Verify connections:

- DC → GPIO 9
- RST → GPIO 25
- BL → GPIO 13
- MOSI → GPIO 10
- SCLK → GPIO 11
- CS → GPIO 8

### Import Errors

Ensure packages are installed for Python 3:

```bash
pip3 list | grep -E "RPi.GPIO|requests|Pillow|spidev"
```

### Network Issues

Test connectivity:

```bash
ping -c 1 8.8.8.8
curl https://asep-battery-counter-api.vercel.app/stats
```

## Environmental Impact Calculations

- **Soil pollution**: 0.02 kg per battery
- **Water pollution**: 0.15 L per battery

These are approximate values for visualization purposes.

## Development

### Testing Without Hardware

Comment out GPIO-dependent code or use GPIO emulation:

```bash
pip3 install fake-rpi
```

Add to top of scripts:

```python
import sys
sys.modules['RPi'] = __import__('fake_rpi.RPi')
sys.modules['RPi.GPIO'] = __import__('fake_rpi.RPi.GPIO')
```

### Draft Files

The `draft/` folder contains standalone examples:

- `display_clock.py`: TFT clock demo
- `st7789_hello_world.py`: Basic display test

## License

This project is part of the ASEP Battery Counter initiative.

## Support

For issues or questions, please contact the project maintainer.
