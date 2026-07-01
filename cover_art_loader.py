import math
import pygame
import io
from pathlib import Path

from config import *


# Refactoring cover art functions into another class
# The goal is to add an option between visualizer 
# and a cassete player animation sort of like the snowskyecho

# These will be replaced by a single function call once I implement the theme loader
# -------------- #
#    Constants
# -------------- #

# dimensions
W = SCREEN_WIDTH
H = SCREEN_HEIGHT

ART_Y   = 0;   ART_H   = 174
TITLE_Y = 174; TITLE_H = 22
SEEK_Y  = 196; SEEK_H  = 24
CTRL_Y  = 220; CTRL_H  = 58
VOL_Y   = 278; VOL_H   = 42

# button rects
_BH = CTRL_H - 12
_BY = CTRL_Y + 6
btn_prev = pygame.Rect(  4, _BY, 43, _BH)
btn_rev  = pygame.Rect( 51, _BY, 43, _BH)
btn_play = pygame.Rect( 98, _BY, 44, _BH)
btn_ff   = pygame.Rect(146, _BY, 43, _BH)
btn_next = pygame.Rect(193, _BY, 43, _BH)
btn_shf  = pygame.Rect( 4,  VOL_Y + 7, 36, VOL_H - 14)
btn_rpt  = pygame.Rect(44,  VOL_Y + 7, 36, VOL_H - 14)

# volume row: [SHF][RPT]  "VOL" [=== bar ===][-][+]
btn_vol_plus  = pygame.Rect(W - 4  - 28, VOL_Y + 7, 28, VOL_H - 14)
btn_vol_minus = pygame.Rect(btn_vol_plus.x - 4 - 28, VOL_Y + 7, 28, VOL_H - 14)

seek_r = pygame.Rect(32, SEEK_Y + 7, W - 64, 10)
vol_r  = pygame.Rect(112, VOL_Y + 17, btn_vol_minus.x - 4 - 112, 8)

# -------------- #
#     Theme
# -------------- #
# to move to a theme file format
# currently using procedurally generated assets
N_BARS = 24
N_SEGS = 16

# palette
BG         = (8,    8,   10)
ART_BG     = (5,    5,    8)
PANEL      = (16,  20,   26)
FG         = (220, 220, 220)
DIM        = (85,  85,   90)
ACCENT     = (70,  190,  85)
BTN_FACE   = (34,  44,   56)
BTN_HI     = (62,  80,  102)
BTN_SH     = (12,  15,   19)
BTN_FG     = (200, 210, 222)
BTN_ACTIVE = (55,  165,  72)
BTN_ACT_FG = (5,    5,    5)
SEEK_BG    = (20,  32,   20)
VOL_BG     = (20,  32,   20)
BORDER     = (30,  42,   30)

# button roundness (corner radius in px, 0 = square corners)
BTN_RADIUS = 0

# Cover Art Panel
def try_draw_cover_art(screen,state):
    # cover art / fallback
    art_rect = pygame.Rect(0, ART_Y, W, ART_H)
    pygame.draw.rect(screen, ART_BG, art_rect)

    cover_bytes = state.get('cover_art')
    
    if cover_bytes:
        try:
            img = pygame.image.load(io.BytesIO(cover_bytes))
            iw, ih = img.get_size()
            # fill: scale so the image covers the full panel, then crop the excess
            scale  = max(W / iw, ART_H / ih)
            new_w  = int(iw * scale)
            new_h  = int(ih * scale)
            img    = pygame.transform.smoothscale(img, (new_w, new_h))
            ox     = (new_w - W)   // 2
            oy     = (new_h - ART_H) // 2
            screen.blit(img, (-ox, ART_Y - oy))
        
        except Exception:
            pass  

# Visualizer Panel
def try_draw_visualizer(screen, wave_t, state):
    # draw visualizer only if state does not have cover art data
    if not state.get('cover_art'):
        pygame.draw.rect(screen, ART_BG, (0, ART_Y, W, ART_H))

        cell_w = W / N_BARS # width of one bar's slot (including gap)
        bar_w  = max(1, int(cell_w) - 2)  # actual drawn bar width, 2px gap between bars
        
        
        cy     = ART_Y + ART_H // 2 # vertical pivot point of the art panel, bars grow up & down from here
        seg_h  = max(1, (ART_H // 2 - 6 - (N_SEGS - 1)) // N_SEGS) # height of each lit segment; subtract space for N_SEGS-1 gaps and a 6px margin
        stride = seg_h + 1        # distance between segment tops (segment + 1px gap)

        for i in range(N_BARS):
            # give each bar a unique frequency and phase so they move independently
            freq  = 1.2 + i * 0.15
            phase = i * 0.55

            # blend two sine waves so the motion looks less mechanical
            # wave_t advances over time; result is always 0.0–1.0
            amp = (abs(math.sin(wave_t * freq + phase)) * 0.7 +
                   abs(math.sin(wave_t * freq * 0.6 + phase + 1.3)) * 0.3)

            # how many segments to light up this frame (at least 1 so bars never vanish)
            filled = max(1, int(amp * N_SEGS))
            bx     = int(i * cell_w + 1)  # left edge of this bar

            for s in range(N_SEGS):
                # brightness ramps from 160 (bottom) to 255 (top) as s increases
                v   = int(160 + s / max(1, N_SEGS - 1) * 95)
                c   = (v, v, v) if s < filled else (12, 12, 14)  # lit vs dark grey

                # upper half: segment s is drawn s+1 steps above centre (so s=0 is closest to cy)
                pygame.draw.rect(screen, c, (bx, cy - (s + 1) * stride, bar_w, seg_h))

                # lower half: mirrored reflection, dimmed to 1/6 brightness
                dim = (v // 6, v // 6, v // 6) if s < filled else (4, 4, 5)
                pygame.draw.rect(screen, dim, (bx, cy + s * stride, bar_w, seg_h))

_tape_img = None  # cached scaled surface

# Cassette Tape Panel: draw static img
# To be replaced with animated implementation soon
def try_draw_tape(screen, _, state):
    global _tape_img

    if state.get('cover_art'):
        return

    pygame.draw.rect(screen, ART_BG, (0, ART_Y, W, ART_H))

    if _tape_img is None:
        src = pygame.image.load(
            str(Path(__file__).parent / 'assets' / 'cassettetape.png')
        ).convert_alpha()
        iw, ih = src.get_size()
        scale   = min(W / iw, ART_H / ih)
        _tape_img = pygame.transform.smoothscale(src, (int(iw * scale), int(ih * scale)))

    iw, ih = _tape_img.get_size()
    screen.blit(_tape_img, ((W - iw) // 2, ART_Y + (ART_H - ih) // 2))
