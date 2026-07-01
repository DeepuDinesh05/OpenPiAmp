from pathlib import Path

# -------------- #
# Screen Settings
# -------------- #
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320
FPS = 60

# -------------- #
# Display Target
# -------------- #
# set USE_FRAMEBUFFER = True to render directly to the SPI LCD
# Leave False for windowed dev testing.
USE_FRAMEBUFFER = True
FRAMEBUFFER_DEVICE = "/dev/fb1"
FULLSCREEN = True
HIDE_CURSOR = True

# -------------- #
# Touch Input
# -------------- #
# On the Pi, set USE_TOUCH = True to read the SPI touchscreen directly via
# evdev and feed it into pygame as synthetic mouse events. 
USE_TOUCH = True
TOUCH_DEVICE = "/dev/input/event0"


# Corner-calibrated via evtest 
# Current values tested for LCD-Show screen orientation tool rotate.sh set to portrait
# Calibration values below are from `evtest /dev/input/event0` on the
# ADS7846 touch controller (see /proc/bus/input/devices to confirm device).
TOUCH_X_MIN, TOUCH_X_MAX = 220, 3830
TOUCH_Y_MIN, TOUCH_Y_MAX = 160, 3700

TOUCH_SWAP_XY  = False
TOUCH_INVERT_X = False
TOUCH_INVERT_Y = False

# -------------- #
# Music Settings
# -------------- #
SUPPORTED_EXTENSIONS = ('*.mp3', '*.flac', '*.ogg', '*.wav')
MUSIC_DIR = Path.home() / "Music"
FAST_FORWARD_DUR = 15
REV_DUR = 15

# -------------- #
#  UI Settings
# -------------- #
TITLE_SCROLL_SPEED = 20
VOLUME_STEP = 0.1
CURRENT_THEME = Path("assets") / "theme_P.json"

