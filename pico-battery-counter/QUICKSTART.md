# Quick Start Guide

## Prerequisites

1. Raspberry Pi 4 with Raspberry Pi OS installed
2. Python 3.7 or higher
3. Internet connection
4. Hardware components connected:
   - IR sensor on GPIO 15
   - LED on GPIO 14
   - ST7789 TFT display on SPI

## Installation Steps

### 1. Enable SPI Interface

```bash
sudo raspi-config
```

- Navigate to: **Interface Options → SPI → Enable**
- Reboot: `sudo reboot`

### 2. Clone or Transfer Project

```bash
cd ~
# If using git:
git clone <repository-url> pico-battery-counter
cd pico-battery-counter

# Or transfer files manually via SCP/USB
```

### 3. Install Dependencies

```bash
cd ~/pico-battery-counter
pip3 install -r requirements.txt
```

If you encounter permission issues:

```bash
sudo pip3 install -r requirements.txt
```

### 4. Configure Device

Edit `config.py` if needed:

```bash
nano config.py
```

Key settings:

- `DEVICE_ID`: Change to unique identifier (e.g., "rpi4_lab1")
- `IR_PIN`: GPIO pin for IR sensor (default: 15)
- `LED_PIN`: GPIO pin for LED (default: 14)

### 5. Test Run

```bash
python3 main.py
```

Expected output:

```
==================================================
Battery Counter - Raspberry Pi 4
==================================================

Initializing hardware...
IR Sensor initialized on GPIO 15
LED initialized on GPIO 14
TFT Display initialized

Starting background sync thread...
Sync thread started

==================================================
System ready! Monitoring IR sensor...
==================================================
```

### 6. Test IR Sensor

Block the IR beam. You should see:

```
*** BATTERY DETECTED! ***
Record added to cache: {'timestamp': 1700000000, 'amount': 1, 'device': 'rpi4_1'}
```

### 7. Verify Syncing

Check the cache file:

```bash
cat cache.json
```

If internet is available, records should sync and the file should become empty `[]`.

### 8. Setup Auto-Start (Optional)

To run on boot:

```bash
sudo nano /etc/systemd/system/battery-counter.service
```

Paste:

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

Enable service:

```bash
sudo systemctl enable battery-counter.service
sudo systemctl start battery-counter.service
```

Check status:

```bash
sudo systemctl status battery-counter.service
```

View logs:

```bash
sudo journalctl -u battery-counter.service -f
```

## Troubleshooting

### GPIO Permission Errors

```bash
sudo usermod -a -G gpio,spi $USER
# Log out and back in
```

### SPI Not Working

Verify SPI is enabled:

```bash
lsmod | grep spi
ls /dev/spi*
```

Should show `spi_bcm2835` and `/dev/spidev0.0`.

### Display Not Initializing

Check connections carefully. Common issues:

- Wrong GPIO pins
- Loose connections
- Power supply insufficient

Disable display temporarily to test other features:

- The code will continue running without the display

### Network Sync Issues

Test API manually:

```bash
curl https://asep-battery-counter-api.vercel.app/stats
```

Check internet:

```bash
ping -c 4 8.8.8.8
```

### Stop the Application

Press `Ctrl+C` to gracefully stop the application.

If running as service:

```bash
sudo systemctl stop battery-counter.service
```

## Next Steps

- Monitor `/var/log/syslog` for system messages
- Check `cache.json` to see pending sync items
- Adjust `DEBOUNCE_MS` in `config.py` if getting false triggers
- Customize display layout in `utils/st7789_display.py`

## Support Files

- `README.md`: Full documentation
- `config.py`: All configuration options
- `cache.json`: Local event storage
- `requirements.txt`: Python dependencies
