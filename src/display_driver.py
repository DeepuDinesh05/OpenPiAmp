import pygame

# ILI9341 fbtft devices expose a 16bpp RGB565 framebuffer.
# this can be verified by running fbset -fb /dev/fb1 -i: rgba 5/11,6/5,5/0,0/0). 
RGB565_MASKS = (0xF800, 0x07E0, 0x001F, 0)

# create RGB_565 masked pygame surface
def make_surface(width, height):
    return pygame.Surface((width, height), depth=16, masks=RGB565_MASKS)


def push(surface, fb_file):
    # pitch = bytes per row as laid out in memory
    # row_bytes = bytes per row the framebuffer actually expects (width * 2 for 16bpp).
    pitch = surface.get_pitch()
    row_bytes = surface.get_width() * 2
    raw = surface.get_buffer().raw

    # framebuffer devices have no concept of a write cursor across frames
    # always start writing from the first byte.
    fb_file.seek(0)

    if pitch == row_bytes:
        # common case: no padding, so the whole buffer can be written in one go
        fb_file.write(raw)
    else:
        # padded case: strip the extra pad bytes from each row before writing
        # prevents disoriented img
        mv = memoryview(raw)
        for y in range(surface.get_height()):
            start = y * pitch
            fb_file.write(mv[start:start + row_bytes])

    # force the write to prevent latency
    fb_file.flush()
