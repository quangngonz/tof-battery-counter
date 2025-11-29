"""
VL6180X Time-of-Flight Sensor Module for Raspberry Pi
Handles I2C communication and distance-based detection
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

from config import TOF_I2C_BUS, TOF_ADDRESS, TOF_XSHUT_PIN, TOF_THRESHOLD_MM


class TOFSensor:
    """
    VL6180X Time-of-Flight Distance Sensor (TOF050C)
    Non-blocking sensor with threshold-based detection
    """

    # Key register addresses
    REG_IDENTIFICATION_MODEL_ID = 0x000
    REG_SYSTEM_INTERRUPT_CLEAR = 0x015
    REG_SYSTEM_FRESH_OUT_OF_RESET = 0x016
    REG_SYSRANGE_START = 0x018
    REG_RESULT_RANGE_STATUS = 0x04D
    REG_RESULT_INTERRUPT_STATUS_GPIO = 0x04F
    REG_RESULT_RANGE_VAL = 0x062

    def __init__(self, bus_number=TOF_I2C_BUS, address=TOF_ADDRESS, xshut_pin=TOF_XSHUT_PIN, threshold_mm=TOF_THRESHOLD_MM):
        """
        Initialize VL6180X sensor

        Args:
            bus_number: I2C bus number (1 for Raspberry Pi 3/4/Zero 2)
            address: I2C address of the sensor (default 0x29)
            xshut_pin: GPIO pin for XSHUT (required for sensor activation)
            threshold_mm: Distance threshold in millimeters
        """
        self.bus_number = bus_number
        self.address = address
        self.xshut_pin = xshut_pin
        self.threshold_mm = threshold_mm
        self.gpio_enabled = False
        self.last_state = False  # False = no object, True = object detected
        self.last_trigger_time = 0
        self.debounce_time = 0.15  # 150ms debounce

        # Setup XSHUT pin to enable sensor
        if GPIO is not None and self.xshut_pin is not None:
            try:
                # Ensure GPIO mode is set (safe to call multiple times)
                try:
                    GPIO.setmode(GPIO.BCM)
                except ValueError:
                    # Mode already set, which is fine
                    pass

                GPIO.setup(self.xshut_pin, GPIO.OUT)
                GPIO.output(self.xshut_pin, GPIO.HIGH)  # Enable sensor
                self.gpio_enabled = True
                print(
                    f"TOF Sensor: XSHUT pin (GPIO {self.xshut_pin}) set HIGH - sensor enabled")
                time.sleep(0.1)  # Give sensor time to power up
            except Exception as e:
                print(
                    f"TOF Sensor: Warning - Could not setup GPIO for XSHUT: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("TOF Sensor: Warning - GPIO not available or xshut_pin not specified")

        # Initialize I2C bus
        self.bus = smbus.SMBus(bus_number)
        print(
            f"TOF Sensor: VL6180X initialized on I2C bus {bus_number}, address 0x{address:02X}")
        print(f"TOF Sensor: Detection threshold set to {threshold_mm}mm")

        # Initialize sensor
        self._init_sensor()

    def _write_byte(self, register, data):
        """Write a byte to a 16-bit register address"""
        self.bus.write_i2c_block_data(
            self.address,
            (register >> 8) & 0xFF,
            [(register & 0xFF), data]
        )

    def _read_byte(self, register):
        """Read a byte from a 16-bit register address"""
        self.bus.write_i2c_block_data(
            self.address,
            (register >> 8) & 0xFF,
            [(register & 0xFF)]
        )
        return self.bus.read_byte(self.address)

    def _init_sensor(self):
        """Initialize the sensor with required settings"""
        try:
            # Check if sensor needs initialization
            fresh_out_of_reset = self._read_byte(
                self.REG_SYSTEM_FRESH_OUT_OF_RESET)

            if fresh_out_of_reset == 1:
                print("TOF Sensor: Loading default settings...")

                # Load mandatory register settings from datasheet
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
                print("TOF Sensor: Default settings loaded successfully")
            else:
                print("TOF Sensor: Already initialized")

        except Exception as e:
            print(f"TOF Sensor: Error during initialization: {e}")
            raise

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
                return -1

            # Read the distance value
            distance = self._read_byte(self.REG_RESULT_RANGE_VAL)

            # Clear the interrupt
            self._write_byte(self.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)

            return distance

        except Exception as e:
            print(f"TOF Sensor: Error reading distance: {e}")
            return -1

    def check(self):
        """
        Non-blocking check for object detection based on threshold

        Returns:
            bool: True if a new object is detected within threshold, False otherwise
        """
        current_time = time.monotonic()

        # Read current distance
        distance = self.read_distance()

        # Determine current state
        current_state = (
            0 < distance < self.threshold_mm) if distance > 0 else False

        # Detect transition from no object to object detected
        if not self.last_state and current_state:
            # Check debounce timing
            if (current_time - self.last_trigger_time) >= self.debounce_time:
                self.last_trigger_time = current_time
                self.last_state = current_state
                print(
                    f"TOF Sensor: Object detected at {distance}mm (threshold: {self.threshold_mm}mm)")
                return True

        self.last_state = current_state
        return False

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
            print(f"TOF Sensor: Error reading model ID: {e}")
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
        try:
            self.bus.close()
            if self.gpio_enabled and GPIO is not None:
                GPIO.output(self.xshut_pin, GPIO.LOW)  # Disable sensor
                GPIO.cleanup(self.xshut_pin)
                print("TOF Sensor: GPIO cleaned up")
        except Exception as e:
            print(f"TOF Sensor: Error during cleanup: {e}")
