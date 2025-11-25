"""
I2C Device Scanner
Attempts to read from all detected I2C addresses to identify the TOF050F sensor
"""

try:
    import smbus2 as smbus
except ImportError:
    import smbus


def scan_and_test_addresses():
    """Scan I2C bus and attempt to read from each device"""
    bus = smbus.SMBus(1)

    # Addresses visible in your i2cdetect output
    detected_addresses = [0x41, 0x42, 0x49, 0x4b, 0x5e, 0x60, 0x75]

    print("Scanning detected I2C devices...\n")
    print("=" * 60)

    for addr in detected_addresses:
        print(f"\nTesting address 0x{addr:02X} ({addr}):")
        print("-" * 40)

        try:
            # Try to read a byte from different registers
            for reg in [0x00, 0x01, 0x02]:
                try:
                    value = bus.read_byte_data(addr, reg)
                    print(f"  Register 0x{reg:02X}: 0x{value:02X} ({value})")
                except:
                    print(f"  Register 0x{reg:02X}: No response")

            # Try reading distance like TOF050F would
            try:
                high = bus.read_byte_data(addr, 0x00)
                low = bus.read_byte_data(addr, 0x01)
                distance = (high << 8) | low
                print(f"  → Possible distance value: {distance} mm")
                if 0 < distance < 3000:
                    print(f"  ✓ This could be your TOF050F sensor!")
            except:
                pass

        except Exception as e:
            print(f"  Error: {e}")

    print("\n" + "=" * 60)
    print("\nLikely candidates for TOF050F will show:")
    print("  - Readable registers at 0x00, 0x01, 0x02")
    print("  - Distance value between 0-3000 mm")

    bus.close()


if __name__ == "__main__":
    print("I2C Device Scanner for TOF050F\n")
    scan_and_test_addresses()
