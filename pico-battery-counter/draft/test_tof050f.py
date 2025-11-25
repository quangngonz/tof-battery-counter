"""
TOF050F Time-of-Flight Sensor Test
Tests I2C communication and distance measurement
"""

import time
try:
    import smbus2 as smbus
except ImportError:
    import smbus


class TOF050FSensor:
    """
    Driver for TOF050F Time-of-Flight Distance Sensor
    Default I2C address: 0x52
    """

    DEFAULT_ADDRESS = 0x52

    # Register addresses
    REG_DISTANCE_HIGH = 0x00
    REG_DISTANCE_LOW = 0x01
    REG_STATUS = 0x02

    def __init__(self, bus_number=1, address=DEFAULT_ADDRESS):
        """
        Initialize TOF050F sensor

        Args:
            bus_number: I2C bus number (1 for Raspberry Pi 3/4/Zero 2)
            address: I2C address of the sensor (default 0x52)
        """
        self.bus = smbus.SMBus(bus_number)
        self.address = address
        print(
            f"TOF050F initialized on I2C bus {bus_number}, address 0x{address:02X}")

    def read_distance(self):
        """
        Read distance measurement from sensor

        Returns:
            int: Distance in millimeters, or -1 on error
        """
        try:
            # Read high and low bytes
            high_byte = self.bus.read_byte_data(
                self.address, self.REG_DISTANCE_HIGH)
            low_byte = self.bus.read_byte_data(
                self.address, self.REG_DISTANCE_LOW)

            # Combine bytes (big-endian)
            distance = (high_byte << 8) | low_byte

            return distance
        except Exception as e:
            print(f"Error reading distance: {e}")
            return -1

    def read_status(self):
        """
        Read sensor status register

        Returns:
            int: Status byte, or -1 on error
        """
        try:
            status = self.bus.read_byte_data(self.address, self.REG_STATUS)
            return status
        except Exception as e:
            print(f"Error reading status: {e}")
            return -1

    def is_available(self):
        """
        Check if sensor is responding on I2C bus

        Returns:
            bool: True if sensor responds, False otherwise
        """
        try:
            self.bus.read_byte_data(self.address, self.REG_STATUS)
            return True
        except:
            return False

    def cleanup(self):
        """
        Close I2C bus connection
        """
        self.bus.close()


def test_continuous_reading(duration_seconds=10):
    """
    Test continuous distance reading for specified duration

    Args:
        duration_seconds: How long to run the test
    """
    print("\n=== TOF050F Continuous Reading Test ===")
    print(f"Duration: {duration_seconds} seconds\n")

    sensor = TOF050FSensor()

    if not sensor.is_available():
        print("ERROR: Sensor not found! Check wiring and I2C address.")
        sensor.cleanup()
        return

    print("Sensor detected successfully!")
    print("Reading distances...\n")

    start_time = time.time()
    count = 0

    try:
        while (time.time() - start_time) < duration_seconds:
            distance = sensor.read_distance()
            status = sensor.read_status()

            if distance >= 0:
                print(
                    f"[{count:04d}] Distance: {distance:4d} mm | Status: 0x{status:02X}")
            else:
                print(f"[{count:04d}] Read error")

            count += 1
            time.sleep(0.1)  # 10 Hz sampling

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")

    finally:
        sensor.cleanup()
        print(
            f"\nTest completed: {count} readings in {time.time() - start_time:.2f} seconds")


def test_detection_threshold(threshold_mm=100):
    """
    Test object detection with a distance threshold

    Args:
        threshold_mm: Distance threshold in millimeters
    """
    print("\n=== TOF050F Detection Threshold Test ===")
    print(f"Threshold: {threshold_mm} mm")
    print("Move objects in front of sensor...\n")

    sensor = TOF050FSensor()

    if not sensor.is_available():
        print("ERROR: Sensor not found! Check wiring and I2C address.")
        sensor.cleanup()
        return

    object_detected = False

    try:
        while True:
            distance = sensor.read_distance()

            if distance >= 0:
                if distance < threshold_mm and not object_detected:
                    print(f"✓ OBJECT DETECTED at {distance} mm")
                    object_detected = True
                elif distance >= threshold_mm and object_detected:
                    print(f"✗ Object moved away ({distance} mm)")
                    object_detected = False

            time.sleep(0.05)  # 20 Hz sampling

    except KeyboardInterrupt:
        print("\n\nTest stopped")

    finally:
        sensor.cleanup()


def test_basic_connection():
    """
    Basic connectivity test - checks if sensor responds
    """
    print("\n=== TOF050F Basic Connection Test ===\n")

    sensor = TOF050FSensor()

    if sensor.is_available():
        print("✓ Sensor connected successfully!")

        # Read a few samples
        print("\nReading 5 samples:")
        for i in range(5):
            distance = sensor.read_distance()
            print(f"  Sample {i+1}: {distance} mm")
            time.sleep(0.2)
    else:
        print("✗ Sensor not found!")
        print("  - Check wiring connections")
        print("  - Verify I2C is enabled (sudo raspi-config)")
        print("  - Check I2C address with: i2cdetect -y 1")

    sensor.cleanup()


if __name__ == "__main__":
    print("TOF050F Sensor Test Suite")
    print("=" * 40)
    print("Select test to run:")
    print("1. Basic connection test")
    print("2. Continuous reading (10 seconds)")
    print("3. Detection threshold test")
    print("4. All tests")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        test_basic_connection()
    elif choice == "2":
        test_continuous_reading(10)
    elif choice == "3":
        threshold = input("Enter threshold in mm (default 100): ").strip()
        threshold = int(threshold) if threshold else 100
        test_detection_threshold(threshold)
    elif choice == "4":
        test_basic_connection()
        test_continuous_reading(10)
        test_detection_threshold(100)
    else:
        print("Invalid choice. Running basic connection test...")
        test_basic_connection()
