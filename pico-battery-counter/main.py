from sensor import IRSensor
from sync import add_record, sync, fetch_stats, load_cache
from tft import TFT
import utime
import machine
import config

sensor = IRSensor(config.IR_PIN)
led_pin = machine.Pin(2, machine.Pin.OUT)

# TODO: Initialize the `TFT` instance with the correct driver and pins before use.
# TODO: Add try/except around network/display operations to avoid hard crashes.

# ---- TFT init (depends on driver) ----
# Example pins for ILI9341:
# spi = machine.SPI(1, baudrate=40000000, sck=machine.Pin(10), mosi=machine.Pin(11))
# display = Display(spi, dc=machine.Pin(8), cs=machine.Pin(9), rst=machine.Pin(12))
# tft = TFT(display)

tft = None   # until you confirm model

last_server_total = 0

while True:
    led_pin.value(1)

    if sensor.check():
        add_record()

    # TODO: Consider batching records or rate-limiting sync calls to save power.

    sync()

    # fetch server stats occasionally
    data = fetch_stats()
    if data:
        last_server_total = data["total"]

    unsynced = len(load_cache())

    total_display = last_server_total + unsynced

    if tft:
        tft.show(total_display)

    utime.sleep(0.05)

    led_pin.value(0)
