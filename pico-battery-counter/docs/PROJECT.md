# 🔋 Battery Counter - Raspberry Pi Edition

**Complete Linux Python 3 conversion for Raspberry Pi 4 & Raspberry Pi Zero 2**

---

## 📦 Project Structure

```
battery-counter/
├── main.py                     # Main application entry point
├── sensor.py                   # IR sensor driver (RPi.GPIO)
├── sync.py                     # Cloud sync & caching
├── tft.py                      # ST7789 display driver
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── install.sh                  # Automated installer
├── test_hardware.py           # Hardware testing utility
├── battery-counter.service    # systemd service file
├── README.md                  # Full documentation
├── QUICKSTART.md             # Fast setup guide
└── CONVERSION.md             # Conversion details
```

---

## 🚀 Quick Start (3 Steps)

### 1. Install

```bash
cd ~/battery-counter
bash install.sh
```

### 2. Configure

```bash
nano config.py  # Edit DEVICE_ID
```

### 3. Run

```bash
python3 main.py
```

**Done!** 🎉

---

## 📋 What Was Converted

| Module      | Status      | Notes                             |
| ----------- | ----------- | --------------------------------- |
| `config.py` | ✅ Complete | Added GPIO mappings, removed WiFi |
| `sensor.py` | ✅ Complete | Uses RPi.GPIO, preserved debounce |
| `sync.py`   | ✅ Complete | Uses requests, removed WiFi mgmt  |
| `tft.py`    | ✅ Complete | Full ST7789 driver + PIL graphics |
| `main.py`   | ✅ Complete | Signal handlers, better logging   |

---

## 🔌 Hardware Connections

### ST7789 Display (SPI)

```
VCC  → 3.3V (Pin 1)
GND  → GND (Pin 6)
MOSI → GPIO10 (Pin 19)
CLK  → GPIO11 (Pin 23)
CS   → GPIO8 (Pin 24)
DC   → GPIO25 (Pin 22)
RST  → GPIO24 (Pin 18)
BL   → GPIO23 (Pin 16)
```

### IR Sensor

```
VCC → 5V (Pin 2)
GND → GND (Pin 6)
OUT → GPIO17 (Pin 11)
```

### Status LED

```
+ → GPIO27 (Pin 13) [with 220Ω resistor]
- → GND (Pin 6)
```

---

## 📦 Dependencies

All installed automatically by `install.sh`:

- **RPi.GPIO** - GPIO control
- **spidev** - SPI communication
- **requests** - HTTP/API calls
- **Pillow (PIL)** - Display graphics

---

## ✅ Features Preserved

- ✅ 150ms IR sensor debounce
- ✅ Local caching of unsynced records
- ✅ Periodic server stats fetching
- ✅ Exact API compatibility
- ✅ Same calculation logic (soil/water)
- ✅ LED status indicator

---

## 🆕 Enhanced Features

- ✨ Complete ST7789 driver implementation
- ✨ Colorful display with TrueType fonts
- ✨ Signal handlers for clean shutdown
- ✨ Hardware testing utility
- ✨ systemd service integration
- ✨ Automated installation script
- ✨ Comprehensive error handling
- ✨ Better logging and diagnostics

---

## 🧪 Testing

Run hardware tests:

```bash
python3 test_hardware.py
```

Tests:

- ✓ Package imports
- ✓ Configuration
- ✓ LED blinking
- ✓ IR sensor detection
- ✓ SPI interface
- ✓ Display output
- ✓ API connectivity
- ✓ Cache operations

---

## 🔧 Service Management

```bash
# Install service
sudo cp battery-counter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable battery-counter.service

# Control service
sudo systemctl start battery-counter    # Start
sudo systemctl stop battery-counter     # Stop
sudo systemctl restart battery-counter  # Restart
sudo systemctl status battery-counter   # Check status

# View logs
sudo journalctl -u battery-counter -f
```

---

## 🌐 API Endpoints

**POST** `/log` - Log battery detection

```json
{
  "timestamp": 1700000000,
  "amount": 1,
  "device_id": "rpi_zero_1"
}
```

**GET** `/stats` - Get statistics

```json
{
  "total": 1234,
  "soil": 24.68,
  "water": 185.1
}
```

Base URL: `https://asep-battery-counter-api.vercel.app`

---

## 📊 Performance

| Metric          | Value           |
| --------------- | --------------- |
| Loop rate       | 20 Hz           |
| Stats fetch     | Every 5 seconds |
| SPI speed       | 40 MHz          |
| Display refresh | 20 Hz           |
| API timeout     | 10 seconds      |

---

## 🛠 Troubleshooting

### Display not working?

```bash
lsmod | grep spi_          # Check SPI enabled
ls -l /dev/spidev*        # Check device exists
sudo raspi-config         # Enable SPI if needed
```

### Permission errors?

```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```

### Can't connect to API?

```bash
ping asep-battery-counter-api.vercel.app
# Check internet connection
```

### Sensor not detecting?

- Check 5V power connection
- Verify GPIO17 connection
- Test sensor LED indicator

---

## 📚 Documentation

- **README.md** - Complete documentation with wiring diagrams
- **QUICKSTART.md** - Fast 5-minute setup guide
- **CONVERSION.md** - Detailed conversion notes
- This file - Quick reference

---

## 🎯 Supported Hardware

- ✅ Raspberry Pi 4 (all models)
- ✅ Raspberry Pi Zero 2 W
- ✅ Raspberry Pi OS (32/64-bit)
- ✅ Python 3.7+

---

## 📝 Configuration

Edit `config.py`:

```python
# Device identification
DEVICE_ID = "rpi_zero_1"  # ← Change this

# GPIO pins (BCM numbering)
IR_PIN = 17
LED_PIN = 27
DC_PIN = 25
RST_PIN = 24
BL_PIN = 23

# Display settings
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
DISPLAY_ROTATION = 0  # 0=portrait, 90=landscape
```

---

## 🔄 Display Information

When running, the display shows:

```
╔══════════════════════════════════╗
║   Battery Counter                ║
║ ──────────────────────────────── ║
║                                  ║
║ Batteries: 1234                  ║
║                                  ║
║ Soil saved:                      ║
║ 24.68 kg                         ║
║                                  ║
║ Water saved:                     ║
║ 185.1 L                          ║
╚══════════════════════════════════╝
```

Colors:

- Title: Yellow
- Batteries: White
- Soil: Green
- Water: Blue

---

## 🔐 File Permissions

Recommended:

```bash
chmod 755 install.sh
chmod 755 test_hardware.py
chmod 644 *.py
chmod 644 requirements.txt
chmod 644 *.md
chmod 644 battery-counter.service
```

---

## 💾 Cache Location

Unsynced records stored at:

```
/var/local/battery_counter_cache.json
```

Automatically created with proper permissions.

---

## 🎓 How It Works

1. **IR Sensor** detects battery → triggers event
2. **Cache** stores detection locally
3. **Sync** uploads cached records to cloud API
4. **Stats** periodically fetches totals from server
5. **Display** shows real-time statistics
6. **LED** blinks to indicate operation

---

## 🔍 Useful Commands

```bash
# Monitor in real-time
python3 main.py

# Run in background
nohup python3 main.py &

# Check if running
ps aux | grep main.py

# View cache
cat /var/local/battery_counter_cache.json

# Test API
curl https://asep-battery-counter-api.vercel.app/stats

# GPIO status
gpio readall
```

---

## 📞 Support

1. Check documentation: `README.md`
2. Run hardware tests: `python3 test_hardware.py`
3. Check logs: `sudo journalctl -u battery-counter -f`
4. Review conversion notes: `CONVERSION.md`

---

## ✨ Ready to Deploy

All files are production-ready and tested. The system maintains complete compatibility with the existing API infrastructure while providing enhanced functionality and reliability on the Raspberry Pi platform.

**Deploy with confidence!** 🚀

---

**Project:** ASEP Battery Counter  
**Platform:** Raspberry Pi 4 / Zero 2  
**Python:** 3.7+  
**Status:** ✅ Production Ready
