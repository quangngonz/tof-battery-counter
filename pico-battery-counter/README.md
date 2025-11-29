# Battery Counter - Raspberry Pi Setup Guide

A battery detection and counting system using a VL6180X Time-of-Flight (TOF) sensor and ST7789 TFT display on Raspberry Pi (32-bit).

## 📋 Table of Contents

- [Hardware Requirements](#hardware-requirements)
- [System Requirements](#system-requirements)
- [Initial Raspberry Pi Setup](#initial-raspberry-pi-setup)
- [Hardware Connections](#hardware-connections)
- [Software Installation](#software-installation)
- [Configuration](#configuration)
- [Service Management](#service-management)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Hardware Requirements

- **Raspberry Pi** (32-bit OS compatible)
  - Tested on: Raspberry Pi 4, Pi 3, Zero 2 W
- **VL6180X Time-of-Flight Distance Sensor (TOF050C)**
  - Non-blocking sensor with threshold-based detection
  - I2C interface
- **ST7789 TFT Display**
  - 240x320 pixels
  - SPI interface
- **LED** (for status indication)
- **MicroSD Card** (16GB+ recommended)
- **Power Supply** (5V, 3A recommended for Pi 4)

---

## 💻 System Requirements

- **OS**: Raspberry Pi OS (32-bit) - Legacy or Bullseye
- **Python**: 3.7+
- **Internet Connection**: Required for cloud sync functionality

---

## 🚀 Initial Raspberry Pi Setup

### 1. Install Raspberry Pi OS (32-bit)

Download and flash **Raspberry Pi OS (32-bit)** to your microSD card:

```bash
# Use Raspberry Pi Imager or download from:
# https://www.raspberrypi.com/software/operating-systems/

# Choose: "Raspberry Pi OS (Legacy, 32-bit)" or "Raspberry Pi OS (32-bit)"
```

### 2. Enable Required Interfaces

After booting your Raspberry Pi, enable I2C and SPI:

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **I2C** → Enable
- **Interface Options** → **SPI** → Enable
- **Finish** and reboot

Or enable via command line:

```bash
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo reboot
```

### 3. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

---

## ⚡ Quick Setup (Automated)

If you want to skip the manual installation steps, use the automated setup script:

```bash
# Navigate to the project directory
cd ~/battery-counter

# Make the setup script executable
chmod +x setup_os.sh

# Run the automated setup
./setup_os.sh
```

**The script will automatically:**
- ✅ Update system packages
- ✅ Enable I2C and SPI interfaces
- ✅ Install all system dependencies
- ✅ Install all Python packages
- ✅ Add your user to required groups (i2c, gpio, spi)
- ✅ Create a `requirements.txt` file
- ✅ Verify all installations
- ✅ Prompt for reboot

After the script completes and you reboot, skip to the [Hardware Connections](#hardware-connections) section.

> **Note**: If you prefer manual installation or want to understand each step, continue with the sections below.

---

## 🔌 Hardware Connections

### VL6180X TOF Sensor (I2C)

| VL6180X Pin | Raspberry Pi Pin | BCM GPIO |
|-------------|------------------|----------|
| VCC         | 3.3V (Pin 1)     | -        |
| GND         | Ground (Pin 6)   | -        |
| SDA         | SDA (Pin 3)      | GPIO 2   |
| SCL         | SCL (Pin 5)      | GPIO 3   |
| XSHUT       | GPIO 17 (Pin 11) | GPIO 17  |

### ST7789 TFT Display (SPI)

| ST7789 Pin | Raspberry Pi Pin | BCM GPIO |
|------------|------------------|----------|
| VCC        | 3.3V (Pin 17)    | -        |
| GND        | Ground (Pin 20)  | -        |
| SCL/SCK    | SCLK (Pin 23)    | GPIO 11  |
| SDA/MOSI   | MOSI (Pin 19)    | GPIO 10  |
| RES/RST    | GPIO 25 (Pin 22) | GPIO 25  |
| DC         | GPIO 9 (Pin 21)  | GPIO 9   |
| BL         | GPIO 13 (Pin 33) | GPIO 13  |

### Status LED

| Component | Raspberry Pi Pin | BCM GPIO |
|-----------|------------------|----------|
| LED (+)   | GPIO 14 (Pin 8)  | GPIO 14  |
| LED (-)   | Ground via 220Ω  | -        |

> **Note**: Use a current-limiting resistor (220Ω - 330Ω) for the LED.

---

## 📦 Software Installation

### 1. Install System Dependencies

```bash
sudo apt install -y python3 python3-pip python3-dev python3-pil \
    i2c-tools git libjpeg-dev zlib1g-dev libfreetype6-dev
```

### 2. Install Python Dependencies

```bash
# Install RPi.GPIO
sudo pip3 install RPi.GPIO

# Install SPI library
sudo pip3 install spidev

# Install I2C library (smbus2)
sudo pip3 install smbus2

# Install Pillow for display graphics
sudo pip3 install Pillow

# Install requests for API communication
sudo pip3 install requests
```

### 3. Clone/Download Project

```bash
# Navigate to your preferred directory
cd ~

# If using git:
git clone <your-repository-url> battery-counter
cd battery-counter

# Or manually copy the project files to ~/battery-counter
```

### 4. Verify I2C and SPI

Check if the TOF sensor is detected:

```bash
sudo i2cdetect -y 1
```

You should see device at address `0x29`.

Check SPI devices:

```bash
ls -l /dev/spidev*
```

You should see `/dev/spidev0.0` and `/dev/spidev0.1`.

---

## ⚙️ Configuration

### Edit Configuration File

Open `config.py` and adjust settings as needed:

```bash
nano config.py
```

**Key Configuration Options:**

```python
# API Endpoints (update with your backend URL)
API_LOG = "https://your-api-url.com/log"
API_STATS = "https://your-api-url.com/stats"

# Device Identification
DEVICE_ID = "rpi4_1"  # Change to unique ID for each device

# GPIO Pins (BCM numbering)
LED_PIN = 14
TOF_XSHUT_PIN = 17

# TOF Sensor Settings
TOF_I2C_BUS = 1
TOF_ADDRESS = 0x29
TOF_THRESHOLD_MM = 100  # Detection threshold in millimeters

# Timing
SYNC_INTERVAL_SECONDS = 5  # How often to sync with cloud
STATS_UPDATE_INTERVAL_LOOPS = 100  # Display update frequency
MAIN_LOOP_SLEEP = 0.05  # Main loop delay (50ms)
```

---

## 🎯 Running the Application

### Manual Testing

Run the application manually to test:

```bash
cd ~/battery-counter
python3 main.py
```

You should see:
- Initialization messages
- TOF sensor detection
- Display updates
- Battery detection events

Press `Ctrl+C` to stop.

---

## 🔄 Service Management

### Setup as System Service

The application can run automatically on boot using systemd.

### 1. Run Setup Script

```bash
cd ~/battery-counter
chmod +x setup_service.sh
./setup_service.sh
```

This script will:
- Update the service file with correct paths
- Install the service to systemd
- Enable auto-start on boot
- Start the service immediately

### 2. Manual Service Commands

**Start the service:**
```bash
sudo systemctl start battery-counter.service
```

**Stop the service:**
```bash
sudo systemctl stop battery-counter.service
```

**Restart the service:**
```bash
sudo systemctl restart battery-counter.service
```

**Check service status:**
```bash
sudo systemctl status battery-counter.service
```

**Enable auto-start on boot:**
```bash
sudo systemctl enable battery-counter.service
```

**Disable auto-start:**
```bash
sudo systemctl disable battery-counter.service
```

**View live logs:**
```bash
sudo journalctl -u battery-counter.service -f
```

**View recent logs:**
```bash
sudo journalctl -u battery-counter.service -n 100
```

### 3. Service File Details

The service file (`battery-counter.service`) contains:

```ini
[Unit]
Description=Battery Counter Display Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi  # Will be auto-updated by setup script
WorkingDirectory=/home/pi/battery-counter
ExecStart=/usr/bin/python3 /home/pi/battery-counter/main.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

---p

## 🐛 Troubleshooting

### I2C Issues

**Sensor not detected:**
```bash
# Check if I2C is enabled
sudo raspi-config

# Verify I2C devices
sudo i2cdetect -y 1

# Check I2C kernel modules
lsmod | grep i2c
```

**Permission issues:**
```bash
# Add user to i2c group
sudo usermod -a -G i2c $USER
# Logout and login again
```

### SPI Issues

**Display not working:**
```bash
# Verify SPI is enabled
ls -l /dev/spidev*

# Check SPI kernel modules
lsmod | grep spi
```

### GPIO Permission Issues

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Install gpio utilities
sudo apt install rpi.gpio-common
```

### Service Not Starting

```bash
# Check service logs
sudo journalctl -u battery-counter.service -n 50

# Check for Python errors
sudo systemctl status battery-counter.service

# Verify file permissions
ls -la ~/battery-counter/main.py

# Make sure main.py is executable
chmod +x ~/battery-counter/main.py
```

### Display Shows Wrong Colors

The ST7789 uses BGR color order. This is handled in the code, but if colors appear wrong:
- Check the `rotation` parameter in `utils/st7789_display.py`
- Verify the display model (some variants use RGB instead of BGR)

### Network/API Issues

```bash
# Test internet connectivity
ping -c 4 8.8.8.8

# Check API endpoints
curl https://your-api-url.com/stats

# View sync logs
sudo journalctl -u battery-counter.service | grep -i sync
```

### Cache File Issues

If the cache file gets corrupted:
```bash
cd ~/battery-counter
rm cache.json
# Service will recreate it automatically
```

---

## 📊 Understanding the System

### How It Works

1. **TOF Sensor**: Continuously monitors distance using VL6180X
2. **Detection**: When object detected within threshold (default 100mm), battery is counted
3. **Caching**: Events are cached locally in `cache.json`
4. **Sync**: Background thread syncs cached events to cloud API every 5 seconds
5. **Display**: TFT shows real-time statistics (total count, soil impact, water impact)
6. **LED**: Blinks on detection, stays on during monitoring

### File Structure

```
battery-counter/
├── main.py                    # Main application entry point
├── config.py                  # Configuration constants
├── cache.json                 # Local event cache (auto-generated)
├── battery-counter.service    # Systemd service file
├── setup_service.sh          # Service installation script
└── utils/
    ├── __init__.py           # Package initialization
    ├── tof_sensor.py         # VL6180X TOF sensor driver
    ├── st7789_display.py     # ST7789 TFT display driver
    └── sync.py               # Cloud sync and caching logic
```
