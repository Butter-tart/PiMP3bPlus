import logging
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import config

# Add lib to path so we can find epdconfig and epd2in13_V4
sys.path.append(os.path.join(config.PROJECT_ROOT, 'lib'))

try:
    # Attempt to import the Waveshare library
    import epd2in13_V4
    import epdconfig
    HAS_EPD = True
except ImportError as e:
    logging.warning(f"Waveshare library components missing: {e}. Running in simulation mode.")
    HAS_EPD = False

class DisplayManager:
    def __init__(self):
        self.width = config.EPD_WIDTH
        self.height = config.EPD_HEIGHT
        self.partial_refresh_count = 0
        self.max_partial_refreshes = 20
        
        self.epd = None
        if HAS_EPD:
            try:
                self.epd = epd2in13_V4.EPD()
                self.epd.init()
                self.epd.Clear(0xFF)
                logging.info("e-Ink display initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize e-Ink display hardware: {e}")
                logging.warning("Falling back to simulation mode.")
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
        if HAS_EPD and self.epd is not None:
            try:
                # For V4, partial refresh is more complex.
                # We need to ensure we don't exceed max partial refreshes
                if partial and self.partial_refresh_count < self.max_partial_refreshes:
                    self.epd.displayPartial(self.epd.getbuffer(self.image))
                    self.partial_refresh_count += 1
                else:
                    self.epd.display(self.epd.getbuffer(self.image))
                    self.partial_refresh_count = 0
            except Exception as e:
                logging.error(f"Display update failed: {e}")
                # Try to re-init on error?
        else:
            # In simulation mode, we can log or save image
            pass

    def sleep(self):
        if HAS_EPD and self.epd is not None:
            try:
                self.epd.sleep()
            except Exception as e:
                logging.error(f"Display sleep failed: {e}")
