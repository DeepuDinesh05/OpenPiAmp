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


# evtest corner-calibration ran to figure out these values
TOUCH_CALIBRATION = {
    'portrait': {
        'x_min': 220, 'x_max': 3830,
        'y_min': 160, 'y_max': 3700,
        'swap_xy': False, 'invert_x': False, 'invert_y': False,
    },
    'landscape': {
        'x_min': 260, 'x_max': 3800,
        'y_min': 320, 'y_max': 3850,
        'swap_xy': True, 'invert_x': True, 'invert_y': False,
    },
}

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
CURRENT_THEME = Path("assets") / "theme_L.json"

