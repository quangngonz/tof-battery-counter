# Quick Start Guide

## 🚀 Fast Installation (5 minutes)

### 1. Copy Files to Raspberry Pi

```bash
# On your Raspberry Pi
mkdir -p ~/battery-counter
cd ~/battery-counter

# Copy all project files to this directory
```

### 2. Run Installation Script

```bash
chmod +x install.sh
bash install.sh
```

The script will:

- Update system packages
- Install dependencies
- Enable SPI
- Configure permissions
- Optionally set up auto-start service

### 3. Configure Device

Edit `config.py`:

```python
DEVICE_ID = "rpi_zero_1"  # ← Change this for each device
```

### 4. Test Hardware

```bash
# Test the application
python3 main.py
```

Press Ctrl+C to stop.

### 5. Set Up Auto-Start (Optional)

If you didn't enable during installation:

```bash
sudo systemctl enable battery-counter.service
sudo systemctl start battery-counter.service
```

---

## 📊 Verify It's Working

### Check Display

You should see:

- Battery Counter title
- Batteries count
- Soil saved (kg)
- Water saved (L)

### Check LED

- Should blink continuously (on/off every 50ms)

### Trigger IR Sensor

- Place battery in front of sensor
- LED should remain on briefly
- Console shows: "Battery detected and logged"
- Display count increments

### Check Logs

```bash
# If running manually
# Output appears in terminal

# If running as service
sudo journalctl -u battery-counter.service -f
```

---

## ⚡ Common Commands

```bash
# Run manually
cd ~/battery-counter
python3 main.py

# Service commands
sudo systemctl start battery-counter.service    # Start
sudo systemctl stop battery-counter.service     # Stop
sudo systemctl restart battery-counter.service  # Restart
sudo systemctl status battery-counter.service   # Check status

# View live logs
sudo journalctl -u battery-counter.service -f

# Test components
python3 -c "from sync import fetch_stats; print(fetch_stats())"
```

---

## 🔧 Troubleshooting

### Display Shows Nothing

1. Check SPI is enabled: `lsmod | grep spi_`
2. Verify connections (DC=GPIO25, RST=GPIO24)
3. Reboot: `sudo reboot`

### Permission Denied

```bash
sudo usermod -a -G gpio $USER
# Log out and back in
```

### No Network Sync

```bash
ping asep-battery-counter-api.vercel.app
# Check internet connection
```

### Sensor Not Detecting

1. Check IR sensor power (5V, GND)
2. Check signal wire (GPIO17 by default)
3. Test sensor LED (should blink when object detected)

---

## 📝 Pin Defaults (BCM numbering)

| Component   | Pin | BCM GPIO |
| ----------- | --- | -------- |
| IR Sensor   | 11  | 17       |
| Status LED  | 13  | 27       |
| Display DC  | 22  | 25       |
| Display RST | 18  | 24       |
| Display BL  | 16  | 23       |
| SPI MOSI    | 19  | 10       |
| SPI CLK     | 23  | 11       |
| SPI CE0     | 24  | 8        |

---

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.
