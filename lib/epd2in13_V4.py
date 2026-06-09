import os
import sys

# Simulation of epdconfig (part of waveshare library)
class epdconfig:
    def __init__(self):
        pass
    def digital_write(self, pin, value):
        pass
    def digital_read(self, pin):
        return 0
    def delay_ms(self, delaytime):
        pass
    def spi_writebyte(self, data):
        pass
    def module_init(self):
        pass
    def module_exit(self):
        pass

# Mock pins
RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24
CS_PIN = 8

# Simulation of epd2in13_V4
class EPD:
    def __init__(self):
        self.width = 122
        self.height = 250
        
    def init(self):
        print("EPD Initialized (Mock)")
        return 0
        
    def getbuffer(self, image):
        # In reality, this converts PIL image to byte buffer
        return []
        
    def display(self, imagebuffer):
        print("EPD Displaying full buffer (Mock)")
        
    def displayPartial(self, imagebuffer):
        print("EPD Displaying partial buffer (Mock)")
        
    def Clear(self, color):
        print(f"EPD Cleared with color {color} (Mock)")
        
    def sleep(self):
        print("EPD Sleep (Mock)")
