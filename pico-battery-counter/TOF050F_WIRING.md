# TOF050F Sensor Wiring Guide

## Overview

The TOF050F is a Time-of-Flight (ToF) distance sensor that uses I2C communication. It measures distances up to 2 meters with millimeter accuracy.

## Pin Connections

### TOF050F Sensor → Raspberry Pi

| TOF050F Pin | Raspberry Pi Pin | GPIO/Function | Description         |
| ----------- | ---------------- | ------------- | ------------------- |
| VIN         | Pin 1 or Pin 17  | 3.3V          | Power supply (3.3V) |
| GND         | Pin 9 or Pin 14  | GND           | Ground              |
| SDA         | Pin 3            | GPIO 2        | I2C Data line       |
| SCL         | Pin 5            | GPIO 3        | I2C Clock line      |
| TXD         | Not connected    | -             | UART TX (not used)  |
| RXD         | Not connected    | -             | UART RX (not used)  |

**Note:** We're using I2C mode (SDA/SCL) since your TFT display already uses SPI pins. The UART pins (TXD/RXD) remain unconnected.

## Wiring Diagram

```text
TOF050F Sensor          Raspberry Pi
┌─────────────┐         ┌─────────────┐
│   ○ VIN ────┼─────────┤   1  ○ ○ 2  │ Pin 1: 3.3V
│   ○ GND ────┼─────────┤   3  ○ ○ 4  │ Pin 3: SDA (GPIO 2)
│   ○ SCL ────┼─────────┤   5  ○ ○ 6  │ Pin 5: SCL (GPIO 3)
│   ○ SDA ────┼─────────┤   7  ○ ○ 8  │ Pin 9: GND
│   ○ RXD     │         │   9  ○ ○ 10 │
│   ○ TXD     │         │   ... (pins already used by TFT)
│             │         │             │
└─────────────┘         └─────────────┘
   (RXD/TXD not connected)
```

### Combined Wiring with TFT Display

Your system now uses:

- **TFT (SPI):** GPIO 8, 9, 10, 11, 13, 25 (from README)
- **IR Sensor:** GPIO 15 (from README)
- **LED:** GPIO 14 (from README)
- **TOF050F (I2C):** GPIO 2, 3 ✓ No conflicts!

## Setup Instructions

### 1. Enable I2C on Raspberry Pi

```bash
sudo raspi-config
```

- Select "Interface Options"
- Select "I2C"
- Enable I2C
- Reboot

### 2. Install Required Packages

```bash
sudo apt-get update
sudo apt-get install -y python3-smbus i2c-tools
pip3 install smbus2
```

### 3. Verify I2C Connection

After wiring, check if the sensor is detected:

```bash
i2cdetect -y 1
```

You should see `52` (the default I2C address) in the output grid.

### 4. Run Test

```bash
cd /Users/quangngo/Documents/Data/Quang's\ Life/asep_project/battery-counter/pico-battery-counter/draft
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
