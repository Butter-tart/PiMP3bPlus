import logging
from . import epdconfig

# Display resolution
EPD_WIDTH       = 122
EPD_HEIGHT      = 250

class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200)   

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logging.debug("e-Paper busy")
        while(epdconfig.digital_read(self.busy_pin) == 1):      #  0: idle, 1: busy
            epdconfig.delay_ms(100)    
        logging.debug("e-Paper busy release")

    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        
        self.reset()

        self.ReadBusy()   
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()   

        self.send_command(0x01) #Driver output control      
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11) #data entry mode       
        self.send_data(0x03)

        self.send_command(0x34) # BorderWavefrom
        self.send_data(0x05)

        self.send_command(0x18) # Temperature Sensor Control
        self.send_data(0x80)

        self.send_command(0x21) #  Display update control
        self.send_data(0x00)
        self.send_data(0x80)

        self.ReadBusy()
        return 0

    def getbuffer(self, image):
        if image.mode != '1':
            image = image.convert('1')
        
        buf = [0xFF] * (int(self.width / 8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        
        if imwidth == self.width and imheight == self.height:
            for y in range(imheight):
                for x in range(imwidth):
                    if pixels[x, y] == 0:
                        buf[int(x / 8) + y * int(self.width / 8)] &= ~(0x80 >> (x % 8))
        elif imwidth == self.height and imheight == self.width:
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int(newx / 8) + newy * int(self.width / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, image):
        self.send_command(0x24)
        for i in range(0, len(image)):
            self.send_data(image[i])   
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xF7)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def displayPartial(self, image):
        # Simplification of partial refresh for V4
        self.send_command(0x24)
        for i in range(0, len(image)):
            self.send_data(image[i])
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xFF) # Partial refresh specific? Actually V4 uses different codes
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def Clear(self, color):
        self.send_command(0x24)
        for i in range(0, int(self.width / 8) * self.height):
            self.send_data(color)
        self.send_command(0x22)
        self.send_data(0xF7)
        self.send_command(0x20)
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x10) #enter deep sleep
        self.send_data(0x01)
        epdconfig.delay_ms(100)
