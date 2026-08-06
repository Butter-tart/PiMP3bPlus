import os
import sys
import time
import logging

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

try:
    import spidev
except ImportError:
    spidev = None

class RaspberryPi:
    # Pin definition
    RST_PIN         = 17
    DC_PIN          = 25
    CS_PIN          = 8
    BUSY_PIN        = 24

    def __init__(self):
        self.SPI = None
        if spidev is not None:
            self.SPI = spidev.SpiDev()
        self.GPIO = GPIO

    def digital_write(self, pin, value):
        if self.GPIO:
            self.GPIO.output(pin, value)

    def digital_read(self, pin):
        if self.GPIO:
            return self.GPIO.input(pin)
        return 0

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        if self.SPI:
            self.SPI.writebytes(data)

    def module_init(self):
        if not self.GPIO or not self.SPI:
            raise RuntimeError("RPi.GPIO or spidev not found. Cannot initialize hardware SPI.")

        spi_device = "/dev/spidev0.0"
        if not os.path.exists(spi_device):
            raise FileNotFoundError(
                f"SPI device {spi_device} not found. Enable SPI in raspi-config and reboot."
            )
        
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)

        # SPI device, bus = 0, device = 0
        try:
            self.SPI.open(0, 0)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Failed to open SPI bus 0 device 0 ({spi_device}). "
                "Enable SPI and verify wiring/HAT connection."
            ) from e
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self):
        logging.info("spi end")
        if self.SPI:
            self.SPI.close()

        logging.info("gpio cleanup")
        if self.GPIO:
            self.GPIO.output(self.RST_PIN, 0)
            self.GPIO.output(self.DC_PIN, 0)
            self.GPIO.cleanup()

implementation = RaspberryPi()

for name in [
    'RST_PIN', 'DC_PIN', 'CS_PIN', 'BUSY_PIN',
    'digital_write', 'digital_read', 'delay_ms', 'spi_writebyte', 'module_init', 'module_exit'
]:
    setattr(sys.modules[__name__], name, getattr(implementation, name))
