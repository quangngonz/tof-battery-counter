#!/usr/bin/env python3
"""
Hardware test script for Battery Counter
Tests each component individually to verify proper setup
"""
import sys
import time


def test_imports():
    """Test if all required packages are installed."""
    print("Testing Python package imports...")
    try:
        import RPi.GPIO as GPIO
        print("  ✓ RPi.GPIO")
    except ImportError as e:
        print(f"  ✗ RPi.GPIO: {e}")
        return False

    try:
        import spidev
        print("  ✓ spidev")
    except ImportError as e:
        print(f"  ✗ spidev: {e}")
        return False

    try:
        import requests
        print("  ✓ requests")
    except ImportError as e:
        print(f"  ✗ requests: {e}")
        return False

    try:
        from PIL import Image, ImageDraw, ImageFont
        print("  ✓ Pillow (PIL)")
    except ImportError as e:
        print(f"  ✗ Pillow: {e}")
        return False

    return True


def test_config():
    """Test if config.py is properly set up."""
    print("\nTesting configuration...")
    try:
        import config
        print(f"  ✓ config.py imported")
        print(f"    Device ID: {config.DEVICE_ID}")
        print(f"    IR Pin: GPIO{config.IR_PIN}")
        print(f"    LED Pin: GPIO{config.LED_PIN}")
        print(f"    DC Pin: GPIO{config.DC_PIN}")
        print(f"    RST Pin: GPIO{config.RST_PIN}")
        return True
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False


def test_led():
    """Test LED functionality."""
    print("\nTesting LED...")
    try:
        import RPi.GPIO as GPIO
        import config

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.LED_PIN, GPIO.OUT)

        print(f"  Blinking LED on GPIO{config.LED_PIN} 5 times...")
        for i in range(5):
            GPIO.output(config.LED_PIN, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(config.LED_PIN, GPIO.LOW)
            time.sleep(0.3)

        GPIO.cleanup(config.LED_PIN)
        print("  ✓ LED test complete - did you see it blink?")
        return True
    except Exception as e:
        print(f"  ✗ LED test failed: {e}")
        return False


def test_ir_sensor():
    """Test IR sensor for 10 seconds."""
    print("\nTesting IR sensor...")
    try:
        from sensor import IRSensor
        import config

        sensor = IRSensor(config.IR_PIN)
        print(f"  Monitoring GPIO{config.IR_PIN} for 10 seconds...")
        print("  Move your hand in front of the sensor...")

        detections = 0
        start_time = time.time()

        while time.time() - start_time < 10:
            if sensor.check():
                detections += 1
                print(f"    Detection #{detections}!")
            time.sleep(0.05)

        sensor.cleanup()
        print(f"  ✓ IR sensor test complete - {detections} detections")
        return True
    except Exception as e:
        print(f"  ✗ IR sensor test failed: {e}")
        return False


def test_spi():
    """Test SPI interface."""
    print("\nTesting SPI interface...")
    try:
        import spidev
        import config

        spi = spidev.SpiDev()
        spi.open(config.SPI_BUS, config.SPI_DEVICE)
        spi.max_speed_hz = 1000000

        # Try a simple write
        spi.writebytes([0x00])
        spi.close()

        print("  ✓ SPI interface accessible")
        return True
    except Exception as e:
        print(f"  ✗ SPI test failed: {e}")
        print("    Make sure SPI is enabled: sudo raspi-config")
        return False


def test_display():
    """Test display functionality."""
    print("\nTesting display...")
    print("  Initializing ST7789 display...")
    try:
        from tft import TFT

        tft = TFT()
        print("  ✓ Display initialized")

        print("  Displaying test pattern...")
        tft.show(42, 0.84, 6.3)
        print("  Test pattern displayed for 5 seconds...")
        print("  Check if display shows: Batteries: 42, Soil: 0.84 kg, Water: 6.3 L")
        time.sleep(5)

        tft.cleanup()
        print("  ✓ Display test complete")
        return True
    except Exception as e:
        print(f"  ✗ Display test failed: {e}")
        return False


def test_api():
    """Test API connectivity."""
    print("\nTesting API connectivity...")
    try:
        from sync import fetch_stats

        print("  Fetching statistics from server...")
        data = fetch_stats()

        if data:
            print(f"  ✓ API connection successful")
            print(f"    Total: {data.get('total', 'N/A')}")
            print(f"    Soil: {data.get('soil', 'N/A')} kg")
            print(f"    Water: {data.get('water', 'N/A')} L")
            return True
        else:
            print("  ✗ Failed to fetch data from API")
            return False
    except Exception as e:
        print(f"  ✗ API test failed: {e}")
        return False


def test_cache():
    """Test cache file operations."""
    print("\nTesting cache functionality...")
    try:
        from sync import load_cache, save_cache

        # Try to load cache
        cache = load_cache()
        print(f"  ✓ Cache loaded - {len(cache)} records")

        # Try to save cache
        save_cache(cache)
        print("  ✓ Cache saved successfully")
        return True
    except Exception as e:
        print(f"  ✗ Cache test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Battery Counter Hardware Test")
    print("=" * 50)

    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("LED", test_led),
        ("IR Sensor", test_ir_sensor),
        ("SPI Interface", test_spi),
        ("Display", test_display),
        ("API Connection", test_api),
        ("Cache System", test_cache),
    ]

    results = {}

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n  ✗ Unexpected error in {name}: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<40} {status}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your system is ready.")
        print("Run the main application with: python3 main.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("See README.md for troubleshooting guidance.")

    print("=" * 50)

    return 0 if passed == total else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
