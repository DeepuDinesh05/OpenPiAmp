import pygame

# ILI9341 fbtft devices expose a 16bpp RGB565 framebuffer (verified via
# `fbset -fb /dev/fb1 -i`: rgba 5/11,6/5,5/0,0/0). Creating the drawing
# surface with these exact masks means its raw bytes are already in the
# framebuffer's native layout, so no per-frame pixel conversion is needed.
RGB565_MASKS = (0xF800, 0x07E0, 0x001F, 0)


def make_surface(width, height):
    return pygame.Surface((width, height), depth=16, masks=RGB565_MASKS)


def push(surface, fb_file):
    pitch = surface.get_pitch()
    row_bytes = surface.get_width() * 2
    raw = surface.get_buffer().raw

    fb_file.seek(0)
    if pitch == row_bytes:
        fb_file.write(raw)
    else:
        mv = memoryview(raw)
        for y in range(surface.get_height()):
            start = y * pitch
            fb_file.write(mv[start:start + row_bytes])
    fb_file.flush()
