import math
import pygame

# dimensions
W, H = 240, 320

ART_Y   = 0;   ART_H   = 174
TITLE_Y = 174; TITLE_H = 22
SEEK_Y  = 196; SEEK_H  = 24
CTRL_Y  = 220; CTRL_H  = 58
VOL_Y   = 278; VOL_H   = 42

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

# button rects
_BH = CTRL_H - 12
_BY = CTRL_Y + 6
btn_prev = pygame.Rect(  4, _BY, 43, _BH)
btn_rew  = pygame.Rect( 51, _BY, 43, _BH)
btn_play = pygame.Rect( 98, _BY, 44, _BH)
btn_ff   = pygame.Rect(146, _BY, 43, _BH)
btn_next = pygame.Rect(193, _BY, 43, _BH)
btn_shf  = pygame.Rect( 4,  VOL_Y + 7, 36, VOL_H - 14)
btn_rpt  = pygame.Rect(44,  VOL_Y + 7, 36, VOL_H - 14)

seek_r = pygame.Rect(32, SEEK_Y + 7, W - 64, 10)
vol_r  = pygame.Rect(84, VOL_Y + 17, W - 88,  8)

# helpers
def fmt(s):
    m, s = divmod(int(max(0, s)), 60)
    return f"{m}:{s:02d}"


def _bevel(surf, rect, face, hi, sh):
    pygame.draw.rect(surf, face, rect)
    x, y, w, h = rect
    pygame.draw.line(surf, hi, (x, y), (x + w - 2, y))
    pygame.draw.line(surf, hi, (x, y), (x, y + h - 2))
    pygame.draw.line(surf, sh, (x, y + h - 1), (x + w - 1, y + h - 1))
    pygame.draw.line(surf, sh, (x + w - 1, y), (x + w - 1, y + h - 1))


def _btn(surf, rect, label, font, pressed=False, active=False):
    _bevel(surf, rect,
           BTN_ACTIVE if active else BTN_FACE,
           BTN_SH if pressed else BTN_HI,
           BTN_HI if pressed else BTN_SH)
    txt = font.render(label, True, BTN_ACT_FG if active else BTN_FG)
    ox = oy = 1 if pressed else 0
    surf.blit(txt, (rect.x + (rect.w - txt.get_width())  // 2 + ox,
                    rect.y + (rect.h - txt.get_height()) // 2 + oy))


def _bar(surf, rect, progress, bg):
    x, y, w, h = rect
    pygame.draw.rect(surf, bg, rect)
    fw = int(w * max(0.0, min(1.0, progress)))
    if fw:
        pygame.draw.rect(surf, ACCENT, (x, y, fw, h))
    pygame.draw.rect(surf, BORDER, rect, 1)


# main draw
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
    track_idx   = state.get('track_idx',   0)
    track_count = state.get('track_count', 0)
    is_playing  = state.get('is_playing',  False)

    screen.fill(BG)

    # visualizer
    pygame.draw.rect(screen, ART_BG, (0, ART_Y, W, ART_H))
    bar_w  = (W - 3 * (N_BARS + 1)) // N_BARS
    cy     = ART_Y + ART_H // 2
    seg_h  = max(1, (ART_H // 2 - 6 - (N_SEGS - 1)) // N_SEGS)
    stride = seg_h + 1
    for i in range(N_BARS):
        freq   = 1.2 + i * 0.15
        phase  = i * 0.55
        amp    = (abs(math.sin(wave_t * freq + phase)) * 0.7 +
                  abs(math.sin(wave_t * freq * 0.6 + phase + 1.3)) * 0.3)
        filled = max(1, int(amp * N_SEGS))
        bx     = 3 + i * (bar_w + 3)
        for s in range(N_SEGS):
            v   = int(160 + s / max(1, N_SEGS - 1) * 95)
            c   = (v, v, v) if s < filled else (12, 12, 14)
            pygame.draw.rect(screen, c, (bx, cy - (s + 1) * stride, bar_w, seg_h))
            dim = (v // 6, v // 6, v // 6) if s < filled else (4, 4, 5)
            pygame.draw.rect(screen, dim, (bx, cy + s * stride, bar_w, seg_h))

    # track counter badge
    if track_count > 0:
        badge = f_small.render(f"{track_idx + 1}/{track_count}", True, FG)
        bw, bh = badge.get_size()
        pygame.draw.rect(screen, (0, 0, 0), (W - bw - 10, 6, bw + 8, bh + 4))
        screen.blit(badge, (W - bw - 6, 8))

    # title
    pygame.draw.rect(screen, PANEL, (0, TITLE_Y, W, TITLE_H))
    screen.set_clip(pygame.Rect(6, TITLE_Y, W - 12, TITLE_H))
    screen.blit(f_title.render(track_name, True, FG), (6, TITLE_Y + 3))
    screen.set_clip(None)

    # seek
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

    # controls
    pygame.draw.rect(screen, PANEL, (0, CTRL_Y, W, CTRL_H))
    _btn(screen, btn_prev, "|<", f_btn)
    _btn(screen, btn_rew,  "<<", f_btn)
    _btn(screen, btn_play, "||" if is_playing else ">", f_btn, active=is_playing)
    _btn(screen, btn_ff,   ">>", f_btn)
    _btn(screen, btn_next, ">|", f_btn)

    # volume / shuffle / repeat
    pygame.draw.rect(screen, PANEL, (0, VOL_Y, W, VOL_H))
    _btn(screen, btn_shf, "SHF", f_small, active=state.get('shuffle', False))
    _btn(screen, btn_rpt, "RPT", f_small, active=state.get('repeat',  False))
    _bar(screen, vol_r, volume, VOL_BG)

    pygame.display.flip()
