"""Main program for Battery Counter with IR sensor and cloud sync."""
from sensor import IRSensor
from sync import add_record, sync, fetch_stats, load_cache
from tft import TFT
import utime
import machine
import config

# Constants
LED_PIN = 2
LOOP_DELAY_MS = 50
STATS_FETCH_INTERVAL = 100

# Initialize hardware
sensor = IRSensor(config.IR_PIN)
led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)

# TODO: Initialize the TFT display with your specific driver and pins
# Example for ILI9341:
# spi = machine.SPI(1, baudrate=40000000, sck=machine.Pin(10), mosi=machine.Pin(11))
# display = Display(spi, dc=machine.Pin(8), cs=machine.Pin(9), rst=machine.Pin(12))
# tft = TFT(display)
tft = None

# State variables
last_server_stats = {'total': 0, 'soil': 0, 'water': 0}
loop_counter = 0

print('Battery Counter started')

while True:
    led_pin.value(1)

    # Check for sensor trigger
    if sensor.check():
        add_record()
        print('Battery detected and logged')

    # Sync cached records to server
    sync()

    # Fetch server stats periodically to reduce API calls
    if loop_counter == STATS_FETCH_INTERVAL:
        data = fetch_stats()
        if data:
            last_server_stats = data

        loop_counter = 0

    # Calculate total including unsynced records
    unsynced_count = len(load_cache())
    total_display = last_server_stats.get('total', 0) + unsynced_count
    soil_display = last_server_stats.get('soil', 0) + (unsynced_count * 0.02)
    water_display = last_server_stats.get('water', 0) + (unsynced_count * 0.15)

    # Update display if available
    if tft:
        try:
            tft.show(total_display, soil_display, water_display)
        except Exception as e:
            print(f'Display error: {e}')

    utime.sleep_ms(LOOP_DELAY_MS)
    led_pin.value(0)

    loop_counter += 1
