import math
import pygame
import io

import cover_art_loader
from config import *

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


# -------------- #
#    Helpers
# -------------- #

# time formatter
def fmt(s):
    m, s = divmod(int(max(0, s)), 60)
    return f"{m}:{s:02d}"

# bevel look for button
def _bevel(surf, rect, face, hi, sh):
    pygame.draw.rect(surf, face, rect, border_radius=BTN_RADIUS)
    x, y, w, h = rect
    pygame.draw.line(surf, hi, (x, y), (x + w - 2, y))
    pygame.draw.line(surf, hi, (x, y), (x, y + h - 2))
    pygame.draw.line(surf, sh, (x, y + h - 1), (x + w - 1, y + h - 1))
    pygame.draw.line(surf, sh, (x + w - 1, y), (x + w - 1, y + h - 1))

def _bar(surf, rect, progress, bg):
    x, y, w, h = rect
    pygame.draw.rect(surf, bg, rect)
    fw = int(w * max(0.0, min(1.0, progress)))
    if fw:
        pygame.draw.rect(surf, ACCENT, (x, y, fw, h))
    pygame.draw.rect(surf, BORDER, rect, 1)

# ----------------- #
# UI Draw Functions
# ----------------- #

# Button element
def _btn(surf, rect, label, font, pressed=False, active=False):
    _bevel(surf, rect,
           BTN_ACTIVE if active else BTN_FACE,
           BTN_SH if pressed else BTN_HI,
           BTN_HI if pressed else BTN_SH)
    txt = font.render(label, True, BTN_ACT_FG if active else BTN_FG)
    ox = oy = 1 if pressed else 0
    surf.blit(txt, (rect.x + (rect.w - txt.get_width())  // 2 + ox,
                    rect.y + (rect.h - txt.get_height()) // 2 + oy))


# Title Panel
def draw_title_panel(screen,track_name,font_title,state):
    pygame.draw.rect(screen, PANEL, (0, TITLE_Y, W, TITLE_H))
    title_surf = font_title.render(track_name, True, FG)
    title_width = title_surf.get_width()
    # clip threshold
    clip_width = W - 12

    if title_width > clip_width:
        scroll_x = int(state.get('scroll_x', 0.0)) % (title_width + 40)
        screen.set_clip(pygame.Rect(6, TITLE_Y, clip_width, TITLE_H))
        screen.blit(title_surf, (6 - scroll_x, TITLE_Y + 3))
        # wrap-around copy so it loops seamlessly
        screen.blit(title_surf, (6 - scroll_x + title_width + 40, TITLE_Y + 3))
        screen.set_clip(None)
    else:
        screen.set_clip(pygame.Rect(6, TITLE_Y, clip_width, TITLE_H))
        screen.blit(title_surf, (6, TITLE_Y + 3))
        screen.set_clip(None)

def seek_bar(screen, f_time, pos_s, dur):
    pygame.draw.rect(screen, PANEL, (0, SEEK_Y, W, SEEK_H))

    # vertically center the time labels within the seek panel
    # draw current position (e.g. "1:23") on the left
    ty = SEEK_Y + (SEEK_H - f_time.get_height()) // 2
    screen.blit(f_time.render(fmt(pos_s), True, DIM), (2, ty))

    # draw total duration (e.g. "3:45") flush to the right edge
    dur_s = f_time.render(fmt(dur), True, DIM)
    screen.blit(dur_s, (W - dur_s.get_width() - 2, ty))

    # unpack the bar rect: left edge, top edge, width, height
    # draw the empty track behind the bar
    x, y, w, h = seek_r
    pygame.draw.rect(screen, SEEK_BG, seek_r)

    # filled = how many pixels to colour: (pos / dur) gives a 0.0–1.0 ratio, scaled to bar width
    # guard against dur=0 to avoid division by zero
    filled = int(w * (pos_s / dur if dur else 0))

    if filled:
        pygame.draw.rect(screen, ACCENT, (x, y, filled, h))

    # playhead handle: a small rect centered on the fill boundary
    # clamped so it never overflows either end of the bar
    kx = max(x, min(x + filled - 3, x + w - 6))
    pygame.draw.rect(screen, ACCENT, (kx, y - 2, 6, h + 4))

    # 1-pixel border around the whole bar
    pygame.draw.rect(screen, BORDER, seek_r, 1)

# Control Panel
def draw_control_panel(screen, font_button, font_general, volume, is_playing, state):
    # controls panel
    pygame.draw.rect(screen, PANEL, (0, CTRL_Y, W, CTRL_H))

    # prev btn
    _btn(screen, btn_prev, "|<", font_button, pressed = state.get('btn_pressed') == 'prev')
    # rev btn
    _btn(screen, btn_rev,  "<<", font_button, pressed = state.get('btn_pressed') == 'rev')
    # play btn
    _btn(screen, btn_play, "||" if is_playing else ">", font_button, active=is_playing)
    # ff btn
    _btn(screen, btn_ff,   ">>", font_button, pressed = state.get('btn_pressed') == 'ff')
    # next btn
    _btn(screen, btn_next, ">|", font_button, pressed = state.get('btn_pressed') == 'next')

    # shuffle / repeat / volume label
    pygame.draw.rect(screen, PANEL, (0, VOL_Y, W, VOL_H))
    _btn(screen, btn_shf, "SHF", font_general, active=state.get('shuffle', False))
    _btn(screen, btn_rpt, "RPT", font_general, active=state.get('repeat',  False))

    vol_label = font_general.render("VOL", True, DIM)
    screen.blit(vol_label, (84, VOL_Y + (VOL_H - vol_label.get_height()) // 2))

    _bar(screen, vol_r, volume, VOL_BG)
    _btn(screen, btn_vol_minus, "-", font_general)
    _btn(screen, btn_vol_plus,  "+", font_general)

# Main draw loop
def draw_frame(screen, fonts, state):
    f_title = fonts['f_title']
    f_time  = fonts['f_time']
    f_btn   = fonts['f_btn']
    f_small = fonts['f_small']

    wave_t      = state.get('wave_t',      0.0)
    track_name  = state.get('track_name',  'No tracks')
    pos_s       = state.get('pos_s',       0.0)
    dur         = state.get('dur',         1.0)
    volume      = state.get('volume',      0.5)
    is_playing  = state.get('is_playing',  False)

    screen.fill(BG)

    # will try to draw cover art but pass if byte array is corrupted
    cover_art_loader.try_draw_cover_art(screen,state)

    # will try to draw visualizer otherwise
    # cover_art_loader.try_draw_visualizer(screen,wave_t,state)
    # placeholder till theme loader is implemented
    cover_art_loader.try_draw_tape(screen, wave_t, state)

    # title
    draw_title_panel(screen,track_name,f_title,state)

    # seek bar
    seek_bar(screen, f_time, pos_s, dur)

    draw_control_panel(screen,f_btn,f_small,volume,is_playing,state)

    pygame.display.flip()
