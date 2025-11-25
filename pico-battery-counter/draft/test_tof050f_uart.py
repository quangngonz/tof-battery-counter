"""
TOF050F Time-of-Flight Sensor Test (UART/Serial Mode)
Uses serial communication (default mode) instead of I2C
Protocol: 115200 baud, 8N1, Modbus RTU
"""

import serial
import time
import struct


class TOF050FSerial:
    """
    Driver for TOF050F via UART/Serial (Modbus RTU protocol)
    Default: 115200 baud, 8 data bits, no parity, 1 stop bit
    """

    def __init__(self, port='/dev/ttyAMA0', baudrate=115200, slave_addr=0x01):
        """
        Initialize TOF050F sensor via UART

        Args:
            port: Serial port (default /dev/ttyAMA0 for RPi GPIO UART)
            baudrate: Baud rate (default 115200)
            slave_addr: Modbus slave address (default 0x01)
        """
        self.port = port
        self.baudrate = baudrate
        self.slave_addr = slave_addr

        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            print(f"TOF050F initialized on {port} at {baudrate} baud")
            print(f"Slave address: 0x{slave_addr:02X}")
        except Exception as e:
            print(f"Error opening serial port: {e}")
            raise

    def _calc_crc(self, data):
        """Calculate CRC-16/MODBUS checksum"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def _build_read_command(self, reg_addr, num_words=1):
        """Build Modbus read command"""
        cmd = bytearray([
            self.slave_addr,  # Slave address
            0x03,              # Function: Read holding registers
            (reg_addr >> 8) & 0xFF,   # Register address high
            reg_addr & 0xFF,           # Register address low
            (num_words >> 8) & 0xFF,  # Number of words high
            num_words & 0xFF           # Number of words low
        ])
        crc = self._calc_crc(cmd)
        cmd.append(crc & 0xFF)         # CRC low
        cmd.append((crc >> 8) & 0xFF)  # CRC high
        return cmd

    def _build_write_command(self, reg_addr, value):
        """Build Modbus write command"""
        cmd = bytearray([
            self.slave_addr,  # Slave address
            0x06,              # Function: Write single register
            (reg_addr >> 8) & 0xFF,   # Register address high
            reg_addr & 0xFF,           # Register address low
            (value >> 8) & 0xFF,      # Data high
            value & 0xFF               # Data low
        ])
        crc = self._calc_crc(cmd)
        cmd.append(crc & 0xFF)         # CRC low
        cmd.append((crc >> 8) & 0xFF)  # CRC high
        return cmd

    def read_distance(self):
        """
        Read distance measurement
        Register 0x0010 contains distance in mm

        Returns:
            int: Distance in millimeters, or -1 on error
        """
        try:
            # Clear buffers
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            # Send read command for register 0x0010
            cmd = self._build_read_command(0x0010, 1)
            self.serial.write(cmd)

            # Wait for response (7 bytes: addr + func + count + 2 data + 2 crc)
            time.sleep(0.05)
            response = self.serial.read(7)

            if len(response) < 7:
                return -1

            # Verify response
            if response[0] != self.slave_addr or response[1] != 0x03:
                return -1

            # Extract distance (bytes 3 and 4)
            distance = (response[3] << 8) | response[4]
            return distance

        except Exception as e:
            print(f"Error reading distance: {e}")
            return -1

    def set_range_mode(self, mode):
        """
        Set ranging mode

        Args:
            mode: 1=High precision (200mm), 2=Middle (400mm), 3=Long (500-600mm)
        """
        try:
            cmd = self._build_write_command(0x0004, mode)
            self.serial.write(cmd)
            time.sleep(0.1)
            response = self.serial.read(8)
            return len(response) == 8
        except Exception as e:
            print(f"Error setting mode: {e}")
            return False

    def set_continuous_output(self, interval_ms):
        """
        Set continuous output mode

        Args:
            interval_ms: Output interval in milliseconds (0 to disable)
        """
        try:
            cmd = self._build_write_command(0x0005, interval_ms)
            self.serial.write(cmd)
            time.sleep(0.1)
            response = self.serial.read(8)
            return len(response) == 8
        except Exception as e:
            print(f"Error setting continuous output: {e}")
            return False

    def is_available(self):
        """Check if sensor responds"""
        distance = self.read_distance()
        return distance >= 0

    def cleanup(self):
        """Close serial port"""
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()


def test_basic_connection():
    """Basic connectivity test"""
    print("\n=== TOF050F Basic Connection Test (UART) ===\n")

    try:
        sensor = TOF050FSerial()

        if sensor.is_available():
            print("✓ Sensor connected successfully!\n")

            # Read a few samples
            print("Reading 5 samples:")
            for i in range(5):
                distance = sensor.read_distance()
                if distance >= 0:
                    print(f"  Sample {i+1}: {distance} mm")
                else:
                    print(f"  Sample {i+1}: Read error")
                time.sleep(0.2)
        else:
            print("✗ Sensor not responding!")
            print("  - Check TX/RX wiring (must be crossed)")
            print("  - Verify power connections")
            print("  - Ensure UART is enabled")

        sensor.cleanup()

    except Exception as e:
        print(f"✗ Error: {e}")


def test_continuous_reading(duration_seconds=10):
    """Test continuous distance reading"""
    print("\n=== TOF050F Continuous Reading Test (UART) ===")
    print(f"Duration: {duration_seconds} seconds\n")

    try:
        sensor = TOF050FSerial()

        if not sensor.is_available():
            print("ERROR: Sensor not found!")
            sensor.cleanup()
            return

        print("Sensor detected successfully!")
        print("Reading distances...\n")

        start_time = time.time()
        count = 0

        while (time.time() - start_time) < duration_seconds:
            distance = sensor.read_distance()

            if distance >= 0:
                print(f"[{count:04d}] Distance: {distance:4d} mm")
            else:
                print(f"[{count:04d}] Read error")

            count += 1
            time.sleep(0.15)  # ~6-7 Hz sampling

        sensor.cleanup()
        print(
            f"\nTest completed: {count} readings in {time.time() - start_time:.2f} seconds")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sensor.cleanup()
    except Exception as e:
        print(f"Error: {e}")


def test_range_modes():
    """Test different ranging modes"""
    print("\n=== TOF050F Range Mode Test ===\n")

    modes = {
        1: "High precision (0-200mm)",
        2: "Middle distance (0-400mm)",
        3: "Long distance (0-600mm)"
    }

    try:
        sensor = TOF050FSerial()

        if not sensor.is_available():
            print("ERROR: Sensor not found!")
            sensor.cleanup()
            return

        for mode_num, mode_name in modes.items():
            print(f"\nTesting {mode_name}...")
            if sensor.set_range_mode(mode_num):
                print(f"  Mode set successfully")
                time.sleep(0.2)

                # Take 3 readings
                for i in range(3):
                    distance = sensor.read_distance()
                    if distance >= 0:
                        print(f"    Reading {i+1}: {distance} mm")
                    time.sleep(0.1)
            else:
                print(f"  Failed to set mode")

        sensor.cleanup()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("TOF050F Sensor Test Suite (UART/Serial Mode)")
    print("=" * 50)
    print("Select test to run:")
    print("1. Basic connection test")
    print("2. Continuous reading (10 seconds)")
    print("3. Range mode test")
    print("4. All tests")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        test_basic_connection()
    elif choice == "2":
        test_continuous_reading(10)
    elif choice == "3":
        test_range_modes()
    elif choice == "4":
        test_basic_connection()
        test_continuous_reading(10)
        test_range_modes()
    else:
        print("Invalid choice. Running basic connection test...")
        test_basic_connection()
