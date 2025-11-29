#!/usr/bin/env python3
"""
Test script for VL6180X Time of Flight sensor using Adafruit CircuitPython library.
This script reads distance (range) and ambient light (lux) measurements from the sensor.
"""

import time
import board
import busio
import adafruit_vl6180x


def main():
    """Main function to initialize and read from VL6180X sensor."""
    try:
        # Create I2C bus
        print("Initializing I2C bus...")
        i2c = busio.I2C(board.SCL, board.SDA)

        # Create sensor instance
        print("Initializing VL6180X sensor...")
        sensor = adafruit_vl6180x.VL6180X(i2c)
        # Optional: Add offset calibration (in millimeters)
        # sensor = adafruit_vl6180x.VL6180X(i2c, offset=10)

        print("VL6180X sensor initialized successfully!")
        print("Starting measurements... (Press Ctrl+C to stop)\n")

        # Main loop: read range and lux every second
        while True:
            # Read the range in millimeters
            range_mm = sensor.range
            print(f"Range: {range_mm}mm")

            # Read range status to check for errors
            status = sensor.range_status
            if status != adafruit_vl6180x.ERROR_NONE:
                print(f"Warning - Range status: {status}")

            # Read the ambient light level
            # Using 1x gain for general purpose measurements
            # Available gain options:
            #   ALS_GAIN_1, ALS_GAIN_1_25, ALS_GAIN_1_67, ALS_GAIN_2_5,
            #   ALS_GAIN_5, ALS_GAIN_10, ALS_GAIN_20, ALS_GAIN_40
            light_lux = sensor.read_lux(adafruit_vl6180x.ALS_GAIN_1)
            print(f"Light (1x gain): {light_lux}lux")

            print("-" * 40)

            # Delay for a second
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\nMeasurement stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the VL6180X sensor is properly connected:")
        print("  - VIN to 3.3V")
        print("  - GND to GND")
        print("  - SDA to SDA (GPIO 2)")
        print("  - SCL to SCL (GPIO 3)")


if __name__ == "__main__":
    main()
