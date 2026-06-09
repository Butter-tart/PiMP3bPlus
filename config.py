import os

# Project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Display settings
EPD_WIDTH = 250
EPD_HEIGHT = 122

# Asset paths
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
MUSIC_DIR = os.path.join(PROJECT_ROOT, 'music')

# Default Font (may need to be adjusted based on system availability)
DEFAULT_FONT = os.path.join(FONTS_DIR, 'Roboto-Medium.ttf')
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 16
FONT_SIZE_LARGE = 20

# Gamepad Mapping (Default for 8BitDo Zero 2 in Android Mode)
# These might need adjustment based on evdev.evtest output
BUTTON_A = 304
BUTTON_B = 305
BUTTON_X = 307
BUTTON_Y = 308
BUTTON_L = 310
BUTTON_R = 311
BUTTON_SELECT = 314
BUTTON_START = 315

# D-Pad (Hat events or specific codes depending on mode)
ABS_HAT0X = 16
ABS_HAT0Y = 17

# Application States
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_SETTINGS = "SETTINGS"
