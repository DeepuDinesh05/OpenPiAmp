import math
import pygame
import io

import src.cover_art_loader as cover_art_loader
import src.theme_loader as theme_loader
from config import CURRENT_THEME

cur_theme = theme_loader.read_theme(CURRENT_THEME)

# -------------- #
#    Layout
# -------------- #
W = cur_theme['W']
H = cur_theme['H']
ORIENTATION = cur_theme['orientation']

ART_Y   = cur_theme['art_y'];   ART_H   = cur_theme['art_h']
TITLE_Y = cur_theme['title_y']; TITLE_H = cur_theme['title_h']
SEEK_Y  = cur_theme['seek_y'];  SEEK_H  = cur_theme['seek_h']
CTRL_Y  = cur_theme['ctrl_y'];  CTRL_H  = cur_theme['ctrl_h']
VOL_Y   = cur_theme['vol_y'];   VOL_H   = cur_theme['vol_h']

btn_prev      = pygame.Rect(*cur_theme['btn_prev'])
btn_rev       = pygame.Rect(*cur_theme['btn_rev'])
btn_play      = pygame.Rect(*cur_theme['btn_play'])
btn_ff        = pygame.Rect(*cur_theme['btn_ff'])
btn_next      = pygame.Rect(*cur_theme['btn_next'])
btn_shf       = pygame.Rect(*cur_theme['btn_shf'])
btn_rpt       = pygame.Rect(*cur_theme['btn_rpt'])
btn_vol_plus  = pygame.Rect(*cur_theme['btn_vol_plus'])
btn_vol_minus = pygame.Rect(*cur_theme['btn_vol_minus'])

seek_r = pygame.Rect(*cur_theme['seek_bar'])
vol_r  = pygame.Rect(*cur_theme['vol_bar'])

# -------------- #
#    Palette
# -------------- #
BG         = cur_theme['BG']
ART_BG     = cur_theme['ART_BG']
PANEL      = cur_theme['PANEL']
FG         = cur_theme['FG']
DIM        = cur_theme['DIM']
ACCENT     = cur_theme['ACCENT']
BTN_FACE   = cur_theme['BTN_FACE']
BTN_HI     = cur_theme['BTN_HI']
BTN_SH     = cur_theme['BTN_SH']
BTN_FG     = cur_theme['BTN_FG']
BTN_ACTIVE = cur_theme['BTN_ACTIVE']
BTN_ACT_FG = cur_theme['BTN_ACT_FG']
SEEK_BG    = cur_theme['SEEK_BG']
VOL_BG     = cur_theme['VOL_BG']
BORDER     = cur_theme['BORDER']
BTN_RADIUS = cur_theme['btn_radius']

# -------------- #
#    Helpers
# -------------- #

def fmt(s):
    m, s = divmod(int(max(0, s)), 60)
    return f"{m}:{s:02d}"

def _bevel(surf, rect, face, hi, sh):
    r = min(BTN_RADIUS, rect.w // 2, rect.h // 2)
    pygame.draw.rect(surf, face, rect, border_radius=r)
    x, y, w, h = rect
    # Lines are inset by r so they don't cross the rounded corners
    pygame.draw.line(surf, hi, (x + r, y),         (x + w - 2 - r, y))
    pygame.draw.line(surf, hi, (x,     y + r),     (x,             y + h - 2 - r))
    pygame.draw.line(surf, sh, (x + r, y + h - 1), (x + w - 1 - r, y + h - 1))
    pygame.draw.line(surf, sh, (x + w - 1, y + r), (x + w - 1,     y + h - 1 - r))

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

def _btn(surf, rect, label, font, pressed=False, active=False):
    _bevel(surf, rect,
           BTN_ACTIVE if active else BTN_FACE,
           BTN_SH if pressed else BTN_HI,
           BTN_HI if pressed else BTN_SH)
    txt = font.render(label, True, BTN_ACT_FG if active else BTN_FG)
    ox = oy = 1 if pressed else 0
    surf.blit(txt, (rect.x + (rect.w - txt.get_width())  // 2 + ox,
                    rect.y + (rect.h - txt.get_height()) // 2 + oy))

def draw_title_panel(screen, track_name, font_title, state):
    pygame.draw.rect(screen, PANEL, (0, TITLE_Y, W, TITLE_H))
    title_surf  = font_title.render(track_name, True, FG)
    title_width = title_surf.get_width()
    clip_width  = W - 12

    if title_width > clip_width:
        scroll_x = int(state.get('scroll_x', 0.0)) % (title_width + 40)
        screen.set_clip(pygame.Rect(6, TITLE_Y, clip_width, TITLE_H))
        screen.blit(title_surf, (6 - scroll_x, TITLE_Y + 3))
        screen.blit(title_surf, (6 - scroll_x + title_width + 40, TITLE_Y + 3))
        screen.set_clip(None)
    else:
        screen.set_clip(pygame.Rect(6, TITLE_Y, clip_width, TITLE_H))
        screen.blit(title_surf, (6, TITLE_Y + 3))
        screen.set_clip(None)

def seek_bar(screen, f_time, pos_s, dur):
    pygame.draw.rect(screen, PANEL, (0, SEEK_Y, W, SEEK_H))

    ty = SEEK_Y + (SEEK_H - f_time.get_height()) // 2
    screen.blit(f_time.render(fmt(pos_s), True, DIM), (2, ty))

    dur_s = f_time.render(fmt(dur), True, DIM)
    screen.blit(dur_s, (W - dur_s.get_width() - 2, ty))

    x, y, w, h = seek_r
    pygame.draw.rect(screen, SEEK_BG, seek_r)

    filled = int(w * (pos_s / dur if dur else 0))
    if filled:
        pygame.draw.rect(screen, ACCENT, (x, y, filled, h))

    kx = max(x, min(x + filled - 3, x + w - 6))
    pygame.draw.rect(screen, ACCENT, (kx, y - 2, 6, h + 4))
    pygame.draw.rect(screen, BORDER, seek_r, 1)

def draw_control_panel(screen, font_button, font_general, volume, is_playing, state):
    pygame.draw.rect(screen, PANEL, (0, CTRL_Y, W, CTRL_H))

    _btn(screen, btn_prev, "|<", font_button, pressed=state.get('btn_pressed') == 'prev')
    _btn(screen, btn_rev,  "<<", font_button, pressed=state.get('btn_pressed') == 'rev')
    _btn(screen, btn_play, "||" if is_playing else ">", font_button, active=is_playing)
    _btn(screen, btn_ff,   ">>", font_button, pressed=state.get('btn_pressed') == 'ff')
    _btn(screen, btn_next, ">|", font_button, pressed=state.get('btn_pressed') == 'next')

    pygame.draw.rect(screen, PANEL, (0, VOL_Y, W, VOL_H))
    _btn(screen, btn_shf, "SHF", font_general, active=state.get('shuffle', False))
    _btn(screen, btn_rpt, "RPT", font_general, active=state.get('repeat',  False))

    vol_label = font_general.render("VOL", True, DIM)
    vol_lx = (btn_rpt.right + vol_r.x - vol_label.get_width()) // 2
    screen.blit(vol_label, (vol_lx, VOL_Y + (VOL_H - vol_label.get_height()) // 2))

    _bar(screen, vol_r, volume, VOL_BG)
    _btn(screen, btn_vol_minus, "-", font_general)
    _btn(screen, btn_vol_plus,  "+", font_general)

def draw_frame(screen, fonts, state):
    f_title = fonts['f_title']
    f_time  = fonts['f_time']
    f_btn   = fonts['f_btn']
    f_small = fonts['f_small']

    wave_t     = state.get('wave_t',     0.0)
    track_name = state.get('track_name', 'No tracks')
    pos_s      = state.get('pos_s',      0.0)
    dur        = state.get('dur',        1.0)
    volume     = state.get('volume',     0.5)
    is_playing = state.get('is_playing', False)

    screen.fill(BG)

    cover_art_loader.try_draw_cover_art(screen, state, cur_theme)
    cover_art_loader.try_draw_visualizer(screen, wave_t, state, cur_theme)

    draw_title_panel(screen, track_name, f_title, state)
    seek_bar(screen, f_time, pos_s, dur)
    draw_control_panel(screen, f_btn, f_small, volume, is_playing, state)
