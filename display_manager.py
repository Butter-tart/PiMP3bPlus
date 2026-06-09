import logging
from PIL import Image, ImageDraw, ImageFont
import config

try:
    # Attempt to import the Waveshare library
    # In a real Pi environment, these would be installed
    from lib import epd2in13_V4
    HAS_EPD = True
except ImportError:
    logging.warning("Waveshare library not found. Running in simulation mode.")
    HAS_EPD = False

class DisplayManager:
    def __init__(self):
        self.width = config.EPD_WIDTH
        self.height = config.EPD_HEIGHT
        self.partial_refresh_count = 0
        self.max_partial_refreshes = 20
        
        if HAS_EPD:
            self.epd = epd2in13_V4.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
        else:
            self.epd = None
            
        self.image = Image.new('1', (self.width, self.height), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)
        
        # Load fonts
        try:
            self.font_small = ImageFont.truetype(config.DEFAULT_FONT, config.FONT_SIZE_SMALL)
            self.font_medium = ImageFont.truetype(config.DEFAULT_FONT, config.FONT_SIZE_MEDIUM)
            self.font_large = ImageFont.truetype(config.DEFAULT_FONT, config.FONT_SIZE_LARGE)
        except Exception:
            logging.warning("Font not found, using default.")
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()

    def clear(self):
        self.draw.rectangle((0, 0, self.width, self.height), fill=255)

    def draw_text(self, x, y, text, font_size="medium", fill=0):
        if font_size == "small":
            font = self.font_small
        elif font_size == "large":
            font = self.font_large
        else:
            font = self.font_medium
            
        self.draw.text((x, y), text, font=font, fill=fill)

    def display(self, partial=False):
        # The e-ink display is usually landscape in our config (250x122)
        # Some waveshare displays require rotation depending on how they are mounted
        if HAS_EPD:
            if partial and self.partial_refresh_count < self.max_partial_refreshes:
                # V4 supports partial refresh
                self.epd.displayPartial(self.epd.getbuffer(self.image))
                self.partial_refresh_count += 1
            else:
                self.epd.display(self.epd.getbuffer(self.image))
                self.partial_refresh_count = 0
        else:
            # In simulation, maybe save to a file or just log
            # self.image.save("display_output.png")
            pass

    def sleep(self):
        if HAS_EPD:
            self.epd.sleep()
