"""
TOF050C-VL6180X Time-of-Flight Sensor Test
Tests I2C communication and distance measurement with VL6180X sensor

Pinout:
- VIN: 3.3V or 5V power
- GND: Ground
- SDA: I2C data line (GPIO 2 on Raspberry Pi)
- SCL: I2C clock line (GPIO 3 on Raspberry Pi)
- INT: Interrupt output (optional, can be left unconnected)
- XSHUT: Shutdown pin (GPIO 17, Pin 11) - must be HIGH to enable sensor
"""

import time
try:
    import smbus2 as smbus
except ImportError:
    import smbus

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


class VL6180X:
    """
    Driver for VL6180X Time-of-Flight Distance Sensor (TOF050C)
    Default I2C address: 0x29 (as per Adafruit documentation)

    This sensor measures distances up to ~500mm (50cm) with 1mm resolution.
    """

    DEFAULT_ADDRESS = 0x29
    XSHUT_PIN = 17  # GPIO 17 (Pin 11)

    # Key register addresses
    REG_IDENTIFICATION_MODEL_ID = 0x000
    REG_SYSTEM_INTERRUPT_CONFIG = 0x014
    REG_SYSTEM_INTERRUPT_CLEAR = 0x015
    REG_SYSTEM_FRESH_OUT_OF_RESET = 0x016
    REG_SYSRANGE_START = 0x018
    REG_SYSRANGE_THRESH_HIGH = 0x019
    REG_SYSRANGE_THRESH_LOW = 0x01A
    REG_SYSRANGE_INTERMEASUREMENT_PERIOD = 0x01B
    REG_SYSRANGE_MAX_CONVERGENCE_TIME = 0x01C
    REG_RESULT_RANGE_STATUS = 0x04D
    REG_RESULT_INTERRUPT_STATUS_GPIO = 0x04F
    REG_RESULT_RANGE_VAL = 0x062

    def __init__(self, bus_number=1, address=DEFAULT_ADDRESS, xshut_pin=None):
        """
        Initialize VL6180X sensor

        Args:
            bus_number: I2C bus number (1 for Raspberry Pi 3/4/Zero 2)
            address: I2C address of the sensor (default 0x29)
            xshut_pin: GPIO pin for XSHUT (default 17). Set to None to skip GPIO control.
        """
        self.xshut_pin = xshut_pin if xshut_pin is not None else self.XSHUT_PIN
        self.gpio_enabled = False

        # Setup XSHUT pin to enable sensor
        if GPIO is not None and self.xshut_pin is not None:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.xshut_pin, GPIO.OUT)
                GPIO.output(self.xshut_pin, GPIO.HIGH)  # Enable sensor
                self.gpio_enabled = True
                print(
                    f"XSHUT pin (GPIO {self.xshut_pin}) set HIGH - sensor enabled")
                time.sleep(0.1)  # Give sensor time to power up
            except Exception as e:
                print(f"Warning: Could not setup GPIO for XSHUT: {e}")
        else:
            print("Warning: RPi.GPIO not available or xshut_pin not specified")

        self.bus = smbus.SMBus(bus_number)
        self.address = address
        print(
            f"VL6180X (TOF050C) initialized on I2C bus {bus_number}, address 0x{address:02X}")

        # Initialize sensor
        self._init_sensor()

    def _write_byte(self, register, data):
        """Write a byte to a 16-bit register address"""
        self.bus.write_i2c_block_data(
            self.address,
            (register >> 8) & 0xFF,
            [(register & 0xFF), data]
        )

    def _write_word(self, register, data):
        """Write a word to a 16-bit register address"""
        self.bus.write_i2c_block_data(
            self.address,
            (register >> 8) & 0xFF,
            [(register & 0xFF), (data >> 8) & 0xFF, data & 0xFF]
        )

    def _read_byte(self, register):
        """Read a byte from a 16-bit register address"""
        self.bus.write_i2c_block_data(
            self.address,
            (register >> 8) & 0xFF,
            [(register & 0xFF)]
        )
        return self.bus.read_byte(self.address)

    def _read_word(self, register):
        """Read a word from a 16-bit register address"""
        self.bus.write_i2c_block_data(
            self.address,
            (register >> 8) & 0xFF,
            [(register & 0xFF)]
        )
        data = self.bus.read_i2c_block_data(self.address, 0x00, 2)
        return (data[0] << 8) | data[1]

    def _init_sensor(self):
        """Initialize the sensor with required settings"""
        try:
            # Check if sensor needs initialization
            fresh_out_of_reset = self._read_byte(
                self.REG_SYSTEM_FRESH_OUT_OF_RESET)

            if fresh_out_of_reset == 1:
                print("Sensor fresh out of reset, loading default settings...")

                # Load default settings (mandatory register settings from datasheet)
                # These are the critical settings for proper operation
                self._write_byte(0x0207, 0x01)
                self._write_byte(0x0208, 0x01)
                self._write_byte(0x0096, 0x00)
                self._write_byte(0x0097, 0xFD)
                self._write_byte(0x00e3, 0x00)
                self._write_byte(0x00e4, 0x04)
                self._write_byte(0x00e5, 0x02)
                self._write_byte(0x00e6, 0x01)
                self._write_byte(0x00e7, 0x03)
                self._write_byte(0x00f5, 0x02)
                self._write_byte(0x00D9, 0x05)
                self._write_byte(0x00DB, 0xCE)
                self._write_byte(0x00DC, 0x03)
                self._write_byte(0x00DD, 0xF8)
                self._write_byte(0x009f, 0x00)
                self._write_byte(0x00a3, 0x3c)
                self._write_byte(0x00b7, 0x00)
                self._write_byte(0x00bb, 0x3c)
                self._write_byte(0x00b2, 0x09)
                self._write_byte(0x00ca, 0x09)
                self._write_byte(0x0198, 0x01)
                self._write_byte(0x01b0, 0x17)
                self._write_byte(0x01ad, 0x00)
                self._write_byte(0x00FF, 0x05)
                self._write_byte(0x0100, 0x05)
                self._write_byte(0x0199, 0x05)
                self._write_byte(0x01a6, 0x1b)
                self._write_byte(0x01ac, 0x3e)
                self._write_byte(0x01a7, 0x1f)
                self._write_byte(0x0030, 0x00)

                # Clear fresh out of reset flag
                self._write_byte(self.REG_SYSTEM_FRESH_OUT_OF_RESET, 0x00)
                print("Default settings loaded successfully")
            else:
                print("Sensor already initialized")

            # Configure interrupt system for range measurements
            # Enable range interrupt on new sample ready (bit 2)
            self._write_byte(self.REG_SYSTEM_INTERRUPT_CONFIG, 0x04)
            
            # Clear any pending interrupts
            self._write_byte(self.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)
            
            # Wait for sensor to stabilize after configuration
            time.sleep(0.05)

        except Exception as e:
            print(f"Error during sensor initialization: {e}")
            raise

    def get_model_id(self):
        """
        Read the model ID (should be 0xB4 for VL6180X)

        Returns:
            int: Model ID byte
        """
        try:
            model_id = self._read_byte(self.REG_IDENTIFICATION_MODEL_ID)
            return model_id
        except Exception as e:
            print(f"Error reading model ID: {e}")
            return -1

    def read_distance(self):
        """
        Read distance measurement from sensor

        Returns:
            int: Distance in millimeters, or -1 on error
        """
        try:
            # Start a single-shot range measurement
            self._write_byte(self.REG_SYSRANGE_START, 0x01)

            # Wait for measurement to complete (poll interrupt status)
            timeout = 100  # 100ms timeout
            start_time = time.time()

            while (time.time() - start_time) < (timeout / 1000.0):
                status = self._read_byte(self.REG_RESULT_INTERRUPT_STATUS_GPIO)
                if (status & 0x04) != 0:  # Check if range measurement is ready
                    break
                time.sleep(0.001)  # 1ms delay
            else:
                print("Timeout waiting for measurement")
                return -1

            # Read the distance value
            distance = self._read_byte(self.REG_RESULT_RANGE_VAL)

            # Clear the interrupt
            self._write_byte(self.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)

            return distance

        except Exception as e:
            print(f"Error reading distance: {e}")
            return -1

    def read_range_status(self):
        """
        Read range status to check for errors

        Returns:
            int: Status code (0 = no error, >0 = various error conditions)
        """
        try:
            status = self._read_byte(self.REG_RESULT_RANGE_STATUS)
            return (status >> 4) & 0x0F  # Error code is in bits 7:4
        except Exception as e:
            print(f"Error reading range status: {e}")
            return -1

    def is_available(self):
        """
        Check if sensor is responding on I2C bus

        Returns:
            bool: True if sensor responds with correct model ID, False otherwise
        """
        try:
            model_id = self.get_model_id()
            return model_id == 0xB4  # Expected model ID for VL6180X
        except:
            return False

    def cleanup(self):
        """
        Close I2C bus connection and cleanup GPIO
        """
        self.bus.close()
        if self.gpio_enabled and GPIO is not None:
            try:
                GPIO.output(self.xshut_pin, GPIO.LOW)  # Disable sensor
                GPIO.cleanup(self.xshut_pin)
                print("GPIO cleaned up")
            except:
                pass


def test_sensor_detection():
    """Test if sensor is present and responding"""
    print("\n" + "="*60)
    print("TEST 1: SENSOR DETECTION")
    print("="*60)

    try:
        sensor = VL6180X()

        if sensor.is_available():
            print("✓ Sensor detected and responding!")
            model_id = sensor.get_model_id()
            print(f"✓ Model ID: 0x{model_id:02X} (Expected: 0xB4)")
            sensor.cleanup()
            return True
        else:
            print("✗ Sensor not detected or wrong model ID")
            sensor.cleanup()
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_single_reading():
    """Test a single distance reading"""
    print("\n" + "="*60)
    print("TEST 2: SINGLE DISTANCE READING")
    print("="*60)

    try:
        sensor = VL6180X()

        print("\nReading distance...")
        distance = sensor.read_distance()
        status = sensor.read_range_status()

        if distance >= 0:
            print(f"✓ Distance: {distance} mm")
            if status == 0:
                print(f"✓ Status: OK (0x{status:02X})")
            else:
                print(f"⚠ Status: Error code 0x{status:02X}")
        else:
            print("✗ Failed to read distance")

        sensor.cleanup()
        return distance >= 0

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_continuous_reading(duration_seconds=10, interval_ms=100):
    """
    Test continuous distance reading for specified duration

    Args:
        duration_seconds: How long to run the test
        interval_ms: Delay between readings in milliseconds
    """
    print("\n" + "="*60)
    print(f"TEST 3: CONTINUOUS READING ({duration_seconds} seconds)")
    print("="*60)
    print("\nPress Ctrl+C to stop early\n")

    try:
        sensor = VL6180X()
        start_time = time.time()
        reading_count = 0
        error_count = 0

        print(f"{'Time (s)':<10} {'Distance (mm)':<15} {'Status':<10}")
        print("-" * 60)

        while (time.time() - start_time) < duration_seconds:
            elapsed = time.time() - start_time
            distance = sensor.read_distance()
            status = sensor.read_range_status()
            reading_count += 1

            if distance >= 0:
                status_text = "OK" if status == 0 else f"Err:0x{status:02X}"
                print(f"{elapsed:<10.2f} {distance:<15} {status_text:<10}")
                if status != 0:
                    error_count += 1
            else:
                print(f"{elapsed:<10.2f} {'READ ERROR':<15} {'FAIL':<10}")
                error_count += 1

            time.sleep(interval_ms / 1000.0)

        print("\n" + "-" * 60)
        print(f"Total readings: {reading_count}")
        print(f"Errors: {error_count}")
        print(
            f"Success rate: {((reading_count - error_count) / reading_count * 100):.1f}%")

        sensor.cleanup()

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sensor.cleanup()
    except Exception as e:
        print(f"\n✗ Error: {e}")


def test_range_limits():
    """Test sensor at different distances"""
    print("\n" + "="*60)
    print("TEST 4: RANGE LIMITS")
    print("="*60)
    print("\nThis test will guide you through testing the sensor at different distances.")
    print("The VL6180X is designed for short to medium range measurements (5-500mm).\n")

    test_distances = [
        ("Very close (5-10mm)", 5, 10),
        ("Close (30-50mm)", 30, 50),
        ("Medium (100-150mm)", 100, 150),
        ("Far (250-300mm)", 250, 300),
        ("Maximum (450-500mm)", 450, 500),
    ]

    try:
        sensor = VL6180X()

        for test_name, min_dist, max_dist in test_distances:
            input(f"\nPosition object at {test_name} and press Enter...")

            # Take 5 readings and average
            readings = []
            for _ in range(5):
                distance = sensor.read_distance()
                if distance >= 0:
                    readings.append(distance)
                time.sleep(0.05)

            if readings:
                avg_distance = sum(readings) / len(readings)
                min_reading = min(readings)
                max_reading = max(readings)
                print(f"  Average: {avg_distance:.1f} mm")
                print(f"  Range: {min_reading}-{max_reading} mm")
                print(
                    f"  Variation: ±{(max_reading - min_reading) / 2:.1f} mm")
            else:
                print("  ✗ No valid readings obtained")

        sensor.cleanup()

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sensor.cleanup()
    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TOF050C-VL6180X SENSOR TEST SUITE")
    print("="*60)
    print("\nConnection:")
    print("  VIN   → 3.3V or 5V")
    print("  GND   → Ground")
    print("  SDA   → GPIO 2 (Pin 3)")
    print("  SCL   → GPIO 3 (Pin 5)")
    print("  INT   → Not connected (optional)")
    print("  XSHUT → GPIO 17 (Pin 11) - REQUIRED for sensor activation")
    print("\nMake sure I2C is enabled on your Raspberry Pi!")
    print("Run: sudo raspi-config → Interface Options → I2C → Enable")

    input("\nPress Enter to start tests...")

    # Run tests in sequence
    if not test_sensor_detection():
        print("\n✗ Sensor detection failed. Check your connections!")
        print("\nTroubleshooting:")
        print("  1. Run 'i2cdetect -y 1' to scan for devices")
        print("  2. Verify VIN and GND connections")
        print("  3. Verify SDA and SCL connections")
        print("  4. Check if I2C is enabled in raspi-config")
        return

    if not test_single_reading():
        print("\n⚠ Single reading test failed, but continuing...")

    # Ask user which additional tests to run
    print("\n" + "="*60)
    print("Select additional tests to run:")
    print("  1. Continuous reading (10 seconds)")
    print("  2. Range limits test (interactive)")
    print("  3. Both")
    print("  4. Skip additional tests")

    choice = input("\nYour choice (1-4): ").strip()

    if choice == "1" or choice == "3":
        test_continuous_reading(duration_seconds=10, interval_ms=100)

    if choice == "2" or choice == "3":
        test_range_limits()

    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
