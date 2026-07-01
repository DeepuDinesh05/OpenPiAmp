import math
import pygame
import io
from pathlib import Path


_tape_img       = None
_tape_img_dims  = (0, 0)

# draw cover art
def try_draw_cover_art(screen, state, theme):
    W, ART_Y, ART_H = theme['W'], theme['art_y'], theme['art_h']
    pygame.draw.rect(screen, theme['ART_BG'], (0, ART_Y, W, ART_H))

    cover_bytes = state.get('cover_art')
    if cover_bytes:
        try:
            img    = pygame.image.load(io.BytesIO(cover_bytes))
            iw, ih = img.get_size()
            scale  = max(W / iw, ART_H / ih)
            new_w  = int(iw * scale)
            new_h  = int(ih * scale)
            img    = pygame.transform.smoothscale(img, (new_w, new_h))
            ox     = (new_w - W)     // 2
            oy     = (new_h - ART_H) // 2
            screen.blit(img, (-ox, ART_Y - oy))
        except Exception:
            pass

# draw visualizer
def try_draw_visualizer(screen, wave_t, state, theme):
    if state.get('cover_art'):
        return

    W, ART_Y, ART_H = theme['W'], theme['art_y'], theme['art_h']
    N_BARS, N_SEGS   = theme['n_bars'], theme['n_segs']

    pygame.draw.rect(screen, theme['ART_BG'], (0, ART_Y, W, ART_H))

    cell_w = W / N_BARS
    bar_w  = max(1, int(cell_w) - 2)
    cy     = ART_Y + ART_H // 2
    seg_h  = max(1, (ART_H // 2 - 6 - (N_SEGS - 1)) // N_SEGS)
    stride = seg_h + 1

    for i in range(N_BARS):
        freq  = 1.2 + i * 0.15
        phase = i * 0.55
        amp   = (abs(math.sin(wave_t * freq + phase)) * 0.7 +
                 abs(math.sin(wave_t * freq * 0.6 + phase + 1.3)) * 0.3)
        filled = max(1, int(amp * N_SEGS))
        bx     = int(i * cell_w + 1)

        for s in range(N_SEGS):
            v   = int(160 + s / max(1, N_SEGS - 1) * 95)
            c   = (v, v, v) if s < filled else (12, 12, 14)
            pygame.draw.rect(screen, c,   (bx, cy - (s + 1) * stride, bar_w, seg_h))
            dim = (v // 6, v // 6, v // 6) if s < filled else (4, 4, 5)
            pygame.draw.rect(screen, dim, (bx, cy + s * stride,       bar_w, seg_h))

# draw tape
def try_draw_tape(screen, wave_t, state, theme):
    global _tape_img, _tape_img_dims

    if state.get('cover_art'):
        return

    W, ART_Y, ART_H = theme['W'], theme['art_y'], theme['art_h']
    pygame.draw.rect(screen, theme['ART_BG'], (0, ART_Y, W, ART_H))

    if _tape_img is None or _tape_img_dims != (W, ART_H):
        src   = pygame.image.load(
            str(Path(__file__).parent / 'assets' / 'cassettetape.png')
        ).convert_alpha()
        iw, ih   = src.get_size()
        scale    = min(W / iw, ART_H / ih)
        _tape_img      = pygame.transform.smoothscale(src, (int(iw * scale), int(ih * scale)))
        _tape_img_dims = (W, ART_H)

    iw, ih = _tape_img.get_size()
    screen.blit(_tape_img, ((W - iw) // 2, ART_Y + (ART_H - ih) // 2))
