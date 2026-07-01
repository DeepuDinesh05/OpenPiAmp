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
# On the Pi, set USE_FRAMEBUFFER = True to render directly to the SPI LCD
# instead of HDMI. Leave False for windowed dev testing.
USE_FRAMEBUFFER = True
FRAMEBUFFER_DEVICE = "/dev/fb1"
FULLSCREEN = True
HIDE_CURSOR = True

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

