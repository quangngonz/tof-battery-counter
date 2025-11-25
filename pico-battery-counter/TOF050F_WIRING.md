# TOF050F Sensor Wiring Guide

## Overview

The TOF050F is a Time-of-Flight (ToF) distance sensor that uses I2C communication. It measures distances up to 2 meters with millimeter accuracy.

## Pin Connections

### Option 1: UART/Serial Mode (Recommended - Default Mode)

| TOF050F Pin | Raspberry Pi Pin | GPIO/Function | Description              |
| ----------- | ---------------- | ------------- | ------------------------ |
| VIN         | Pin 1 or Pin 17  | 3.3V          | Power supply (3.3V)      |
| GND         | Pin 9 or Pin 14  | GND           | Ground                   |
| TX          | Pin 10           | GPIO 15 (RXD) | UART TX → Pi RX (cross!) |
| RX          | Pin 8            | GPIO 14 (TXD) | UART RX → Pi TX (cross!) |
| SDA         | Not connected    | -             | (I2C not used)           |
| SCL         | Not connected    | -             | (I2C not used)           |

**⚠️ Important:** TX/RX must be **crossed**: Sensor TX → Pi RX, Sensor RX → Pi TX

**Note:** The sensor operates in serial mode by default (115200 baud). This is easier and more reliable than I2C mode.

### Option 2: I2C Mode (Requires Configuration)

| TOF050F Pin | Raspberry Pi Pin | GPIO/Function | Description         |
| ----------- | ---------------- | ------------- | ------------------- |
| VIN         | Pin 1 or Pin 17  | 3.3V          | Power supply (3.3V) |
| GND         | Pin 9 or Pin 14  | GND           | Ground              |
| SDA         | Pin 3            | GPIO 2        | I2C Data line       |
| SCL         | Pin 5            | GPIO 3        | I2C Clock line      |
| TX          | Not connected    | -             | (UART not used)     |
| RX          | Not connected    | -             | (UART not used)     |

**Note:** To use I2C mode, you must first configure the sensor via serial command. See section below.

## Wiring Diagrams

### UART Mode (Recommended)

```text
TOF050F Sensor          Raspberry Pi
┌─────────────┐         ┌─────────────┐
│   ○ VIN ────┼─────────┤   1  ○ ○ 2  │ Pin 1: 3.3V
│   ○ GND ────┼─────────┤   3  ○ ○ 4  │
│   ○ SCL     │         │   5  ○ ○ 6  │
│   ○ SDA     │         │   7  ○ ○ 8  │ Pin 8: TXD (GPIO 14) ──┐
│   ○ RX  ────┼─────────┤   9  ○ ○ 10 │ Pin 10: RXD (GPIO 15)  │
│   ○ TX  ────┼─────────┤             │                        │
│             │    ┌────┴─────────────┘                        │
└─────────────┘    │  Pin 9 or 14: GND                         │
                   └───────────────────────────────────────────┘
                          (TX/RX are crossed!)
```

### Combined Wiring with TFT Display

**⚠️ CONFLICT DETECTED:** GPIO 14 and GPIO 15 are used by both IR sensor and UART!

Your current system uses:

- **TFT (SPI):** GPIO 8, 9, 10, 11, 13, 25
- **IR Sensor:** GPIO 15 ❌ (conflicts with UART RX)
- **LED:** GPIO 14 ❌ (conflicts with UART TX)
- **TOF050F (UART):** GPIO 14 (TX), 15 (RX)

**Solutions:**

1. **Use I2C mode instead** - GPIO 2, 3 (no conflicts)
2. **Move IR sensor and LED** to different pins (e.g., GPIO 17, 27)
3. **Use USB-to-Serial adapter** for TOF050F instead of GPIO UART

## Setup Instructions

### For UART Mode (Default)

#### 1. Enable UART on Raspberry Pi

```bash
sudo raspi-config
```

- Select "Interface Options"
- Select "Serial Port"
- "Would you like a login shell accessible over serial?" → **No**
- "Would you like the serial port hardware enabled?" → **Yes**
- Reboot

#### 2. Disable Bluetooth (frees up /dev/ttyAMA0)

```bash
sudo nano /boot/config.txt
```

Add this line at the end:

```
dtoverlay=disable-bt
```

Disable Bluetooth service:

```bash
sudo systemctl disable hciuart
sudo reboot
```

#### 3. Install Required Packages

```bash
pip3 install pyserial
```

#### 4. Run Test

```bash
cd ~/Documents/asep-battery-counter/pico-battery-counter/draft
python3 test_tof050f_uart.py
```

---

### For I2C Mode (Advanced)

#### 1. Enable I2C

```bash
sudo raspi-config
```

- Select "Interface Options"
- Select "I2C"
- Enable I2C
- Reboot

#### 2. Install Required Packages

```bash
sudo apt-get update
sudo apt-get install -y python3-smbus i2c-tools
pip3 install smbus2
```

#### 3. Switch Sensor to I2C Mode

First, connect via UART and send this command:

```
01 06 00 09 00 01 98 08
```

This switches the sensor from serial to I2C mode.

#### 4. Verify I2C Connection

```bash
i2cdetect -y 1
```

You should see `52` (0x52) in the output grid.

#### 5. Run Test

```bash
python3 test_tof050f.py
```

## Important Notes

- **Voltage:** Use 3.3V only, not 5V! The TOF050F is not 5V tolerant.
- **Pull-up Resistors:** The Raspberry Pi has built-in I2C pull-up resistors, so external resistors are not needed.
- **I2C Address:** Default is 0x52. If your sensor has a different address, update it in the test code.
- **Cable Length:** Keep I2C cables short (< 30cm) for reliable communication.

## Troubleshooting

| Issue                 | Solution                                                      |
| --------------------- | ------------------------------------------------------------- |
| Sensor not detected   | Check wiring, ensure I2C is enabled, verify power supply      |
| Intermittent readings | Shorten cables, check for loose connections                   |
| Always reads 0 or max | Check sensor orientation, ensure nothing blocking the sensor  |
| I2C errors            | Add 4.7kΩ pull-up resistors to SDA and SCL if cables are long |

## Example Usage in Code

```python
from test_tof050f import TOF050FSensor

sensor = TOF050FSensor()
distance = sensor.read_distance()
print(f"Distance: {distance} mm")
sensor.cleanup()
```

asephntl@raspberrypi:~/Documents/asep-battery-counter/pico-battery-counter/draft $ python test_tof050f.py
TOF050F Sensor Test Suite
========================================
Select test to run:

1. Basic connection test
2. Continuous reading (10 seconds)
3. Detection threshold test
4. All tests

Enter choice (1-4): 2

=== TOF050F Continuous Reading Test ===
Duration: 10 seconds

TOF050F initialized on I2C bus 1, address 0x52
ERROR: Sensor not found! Check wiring and I2C address.
asephntl@raspberrypi:~/Documents/asep-battery-counter/pico-battery-counter/draft $ i2cdetect -y 1
0 1 2 3 4 5 6 7 8 9 a b c d e f
00: -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- 41 42 -- -- -- -- -- -- 49 -- 4b -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- 5e --
60: 60 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- 75 -- --
