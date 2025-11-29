"""
Debug version of TOF050C test to diagnose measurement timeout issue
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


class VL6180X_Debug:
    """Debug version with verbose output"""
    
    DEFAULT_ADDRESS = 0x29
    XSHUT_PIN = 17
    
    # Key register addresses
    REG_IDENTIFICATION_MODEL_ID = 0x000
    REG_SYSTEM_INTERRUPT_CONFIG = 0x014
    REG_SYSTEM_INTERRUPT_CLEAR = 0x015
    REG_SYSTEM_FRESH_OUT_OF_RESET = 0x016
    REG_SYSRANGE_START = 0x018
    REG_RESULT_RANGE_STATUS = 0x04D
    REG_RESULT_INTERRUPT_STATUS_GPIO = 0x04F
    REG_RESULT_RANGE_VAL = 0x062
    
    def __init__(self, bus_number=1, address=DEFAULT_ADDRESS):
        self.gpio_enabled = False
        
        # Setup GPIO
        if GPIO is not None:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.XSHUT_PIN, GPIO.OUT)
                GPIO.output(self.XSHUT_PIN, GPIO.HIGH)
                self.gpio_enabled = True
                print(f"✓ XSHUT pin (GPIO {self.XSHUT_PIN}) set HIGH")
                time.sleep(0.1)
            except Exception as e:
                print(f"✗ GPIO setup failed: {e}")
        
        self.bus = smbus.SMBus(bus_number)
        self.address = address
        print(f"✓ I2C bus {bus_number} opened, address 0x{address:02X}")
        
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
        """Initialize sensor with mandatory settings"""
        try:
            fresh = self._read_byte(self.REG_SYSTEM_FRESH_OUT_OF_RESET)
            print(f"Fresh out of reset register: 0x{fresh:02X}")
            
            if fresh == 1:
                print("Loading mandatory settings...")
                
                # Mandatory settings from datasheet
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
                
                # Clear fresh out of reset
                self._write_byte(self.REG_SYSTEM_FRESH_OUT_OF_RESET, 0x00)
                print("✓ Mandatory settings loaded")
                
                # Wait a bit after initialization
                time.sleep(0.1)
            else:
                print("✓ Sensor already initialized")
            
            # Configure interrupt system for range measurements
            # Enable range interrupt on new sample ready (bit 2)
            self._write_byte(self.REG_SYSTEM_INTERRUPT_CONFIG, 0x04)
            
            # Clear any pending interrupts
            self._write_byte(self.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)
            
            # Wait for sensor to stabilize after configuration
            time.sleep(0.05)
                
        except Exception as e:
            print(f"✗ Init error: {e}")
            raise
    
    def read_distance_debug(self):
        """Read distance with detailed debugging output"""
        print("\n" + "="*60)
        print("DETAILED MEASUREMENT DEBUG")
        print("="*60)
        
        try:
            # Check initial status
            print("\n1. Checking initial register states...")
            int_status_before = self._read_byte(self.REG_RESULT_INTERRUPT_STATUS_GPIO)
            range_status_before = self._read_byte(self.REG_RESULT_RANGE_STATUS)
            print(f"   Interrupt status before: 0x{int_status_before:02X} (binary: {int_status_before:08b})")
            print(f"   Range status before: 0x{range_status_before:02X}")
            
            # Clear any previous interrupts
            print("\n2. Clearing previous interrupts...")
            self._write_byte(self.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)
            time.sleep(0.01)
            
            int_status_after_clear = self._read_byte(self.REG_RESULT_INTERRUPT_STATUS_GPIO)
            print(f"   Interrupt status after clear: 0x{int_status_after_clear:02X} (binary: {int_status_after_clear:08b})")
            
            # Start measurement
            print("\n3. Starting range measurement...")
            self._write_byte(self.REG_SYSRANGE_START, 0x01)
            print("   Start command sent (0x01 to register 0x018)")
            
            # Poll for completion with detailed output
            print("\n4. Polling for measurement completion...")
            print("   Waiting for bit 2 (0x04) to be set in interrupt status register...")
            print(f"   {'Time (ms)':<12} {'Int Status':<15} {'Bit 2':<10} {'Range Status':<15}")
            print("   " + "-"*60)
            
            timeout_ms = 200
            start_time = time.time()
            poll_count = 0
            
            while (time.time() - start_time) < (timeout_ms / 1000.0):
                elapsed_ms = (time.time() - start_time) * 1000
                int_status = self._read_byte(self.REG_RESULT_INTERRUPT_STATUS_GPIO)
                range_status = self._read_byte(self.REG_RESULT_RANGE_STATUS)
                bit2_set = (int_status & 0x04) != 0
                
                poll_count += 1
                
                # Print every 10ms or when bit changes
                if poll_count % 10 == 0 or bit2_set:
                    print(f"   {elapsed_ms:<12.1f} 0x{int_status:02X} ({int_status:08b}) {bit2_set!s:<10} 0x{range_status:02X}")
                
                if bit2_set:
                    print(f"\n   ✓ Measurement ready after {elapsed_ms:.1f}ms ({poll_count} polls)")
                    
                    # Read distance
                    distance = self._read_byte(self.REG_RESULT_RANGE_VAL)
                    error_code = (range_status >> 4) & 0x0F
                    
                    print(f"\n5. Reading results...")
                    print(f"   Distance value: {distance} mm")
                    print(f"   Error code: 0x{error_code:X} ({'OK' if error_code == 0 else 'ERROR'})")
                    
                    # Clear interrupt
                    self._write_byte(self.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)
                    print(f"   Interrupt cleared")
                    
                    return distance
                
                time.sleep(0.001)  # 1ms delay
            
            # Timeout occurred
            print(f"\n   ✗ TIMEOUT after {timeout_ms}ms ({poll_count} polls)")
            print(f"   Final interrupt status: 0x{int_status:02X} (binary: {int_status:08b})")
            print(f"   Final range status: 0x{range_status:02X}")
            
            # Try to read distance anyway
            distance = self._read_byte(self.REG_RESULT_RANGE_VAL)
            print(f"   Distance register value (despite timeout): {distance} mm")
            
            return -1
            
        except Exception as e:
            print(f"\n✗ Exception during measurement: {e}")
            import traceback
            traceback.print_exc()
            return -1
    
    def cleanup(self):
        """Cleanup resources"""
        self.bus.close()
        if self.gpio_enabled and GPIO is not None:
            GPIO.output(self.XSHUT_PIN, GPIO.LOW)
            GPIO.cleanup(self.XSHUT_PIN)
            print("\n✓ GPIO cleaned up")


def main():
    print("\n" + "="*60)
    print("VL6180X DEBUG TEST")
    print("="*60)
    print("\nThis will run a detailed diagnostic of the measurement process")
    
    input("\nPress Enter to start...")
    
    try:
        sensor = VL6180X_Debug()
        
        # Check model ID
        print("\n" + "="*60)
        print("MODEL ID CHECK")
        print("="*60)
        model_id = sensor._read_byte(sensor.REG_IDENTIFICATION_MODEL_ID)
        print(f"Model ID: 0x{model_id:02X} (Expected: 0xB4)")
        
        if model_id != 0xB4:
            print("✗ Wrong model ID!")
            sensor.cleanup()
            return
        
        # Try reading distance with debug output
        distance = sensor.read_distance_debug()
        
        if distance >= 0:
            print(f"\n{'='*60}")
            print(f"✓ SUCCESS: Distance = {distance} mm")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"✗ FAILED: Could not read distance")
            print(f"{'='*60}")
        
        sensor.cleanup()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
