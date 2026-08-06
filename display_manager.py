import logging
import sys
import os
import importlib.util
from PIL import Image, ImageDraw, ImageFont
import config

LIB_DIR = os.path.join(config.PROJECT_ROOT, 'lib')
EPD_IMPORT_ERROR = None
HAS_EPD = False
epd2in13_V4 = None
epdconfig = None


def _load_module_from_path(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create spec for {module_name} at {module_path}")
    module = importlib.util.module_from_spec(spec)
    # Register before execution so module code can access sys.modules[__name__].
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_waveshare_modules():
    epdconfig_path = os.path.join(LIB_DIR, "epdconfig.py")
    epd_driver_path = os.path.join(LIB_DIR, "epd2in13_V4.py")

    if not os.path.exists(epdconfig_path):
        raise ImportError(f"Missing driver file: {epdconfig_path}")
    if not os.path.exists(epd_driver_path):
        raise ImportError(f"Missing driver file: {epd_driver_path}")

    # Ensure local driver directory can resolve sibling imports if needed.
    if LIB_DIR not in sys.path:
        sys.path.insert(0, LIB_DIR)

    logging.info(f"Loading e-Ink drivers from: {LIB_DIR}")
    loaded_epdconfig = _load_module_from_path("epdconfig", epdconfig_path)
    loaded_epd2 = _load_module_from_path("epd2in13_V4", epd_driver_path)
    return loaded_epd2, loaded_epdconfig


try:
    epd2in13_V4, epdconfig = _load_waveshare_modules()
    HAS_EPD = True
except Exception as e:
    EPD_IMPORT_ERROR = str(e)
    logging.warning(f"Waveshare library import failed: {e}. Running in simulation mode.")
    HAS_EPD = False

class DisplayManager:
    def __init__(self):
        self.width = config.EPD_WIDTH
        self.height = config.EPD_HEIGHT
        self.partial_refresh_count = 0
        self.max_partial_refreshes = 20
        self.simulation_reason = None
        
        self.epd = None
        if HAS_EPD:
            try:
                self.epd = epd2in13_V4.EPD()
                self.epd.init()
                self.epd.Clear(0xFF)
                logging.info("e-Ink display initialized successfully.")
            except Exception as e:
                self.simulation_reason = str(e)
                logging.error(f"Failed to initialize e-Ink display hardware: {e}")
                logging.error(
                    "Common causes: missing RPi.GPIO/spidev packages, SPI disabled, "
                    "or running outside Raspberry Pi hardware."
                )
                logging.warning("Falling back to simulation mode.")
                self.epd = None
        else:
            self.simulation_reason = EPD_IMPORT_ERROR
        
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

    def is_hardware_active(self):
        return HAS_EPD and self.epd is not None
