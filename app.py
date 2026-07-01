import pygame
import random
import os

import src.ui as ui
import src.display_driver as display_driver
from config import *
from src.music_loader import *

# SDL has no video driver that can reach /dev/fb1, fbdev doesn't exist in SDL2 
# So we run SDL_VIDEODRIVER=dummy just for pygame's surfaces/fonts and write raw image data to framebuffer
if USE_FRAMEBUFFER:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

pygame.init()
pygame.display.set_caption("OpenPiAmp")

fonts = {
    'f_title': pygame.font.Font(None, 22),
    'f_time':  pygame.font.Font(None, 16),
    'f_btn':   pygame.font.Font(None, 20),
    'f_small': pygame.font.Font(None, 15),
}

if USE_FRAMEBUFFER:
    # dummy driver still needs *a* display mode set for pygame's event/font
    # subsystems; actual pixels go to fb_screen (/dev/fb1)
    pygame.display.set_mode((1, 1))
    fb_screen = display_driver.make_surface(ui.W, ui.H)
    fb_device = open(FRAMEBUFFER_DEVICE, "wb")
    screen = fb_screen
else:
    screen = pygame.display.set_mode((ui.W, ui.H), pygame.FULLSCREEN if FULLSCREEN else 0)
    pygame.mouse.set_visible(not HIDE_CURSOR)
    fb_device = None

if USE_TOUCH:
    import src.touch_input as touch_input
    calib = TOUCH_CALIBRATION[ui.ORIENTATION]
    touch_bridge = touch_input.TouchWrapper(
        TOUCH_DEVICE, ui.W, ui.H,
        calib['x_min'], calib['x_max'], calib['y_min'], calib['y_max'],
        swap_xy=calib['swap_xy'], invert_x=calib['invert_x'], invert_y=calib['invert_y'],
    )
    touch_bridge.start()

clock  = pygame.time.Clock()

# init default state
state = {
    'track_name':  "-",
    'wave_t':      0.0,
    'pos_s':       2.0,
    'dur':         265.0,
    'volume':      0.7,
    'track_idx':   0,
    'scroll_x' :   0,
    'is_playing':  True,
    'shuffle':     False,
    'repeat':      False,
    'btn_pressed': None,
    'cover_art' :  None
}

# scan music directory and init state with actual music data
tracks = scan(MUSIC_DIR,state)
pygame.mixer.music.set_volume(state['volume'])

running = True
try:
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse button support only, to be translated into touch input
            # Have to finalize driver support
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                p = event.pos

                # Volume button minus
                if ui.btn_vol_minus.collidepoint(p):
                    state['volume'] = max(0.0, state['volume'] - VOLUME_STEP)
                    pygame.mixer.music.set_volume(state['volume'])

                # Volume button plus
                elif ui.btn_vol_plus.collidepoint(p):
                    state['volume'] = min(1.0, state['volume'] + VOLUME_STEP)
                    pygame.mixer.music.set_volume(state['volume'])

                # Play button
                elif ui.btn_play.collidepoint(p):
                    state['is_playing'] = not state['is_playing']
                    # print(state['is_playing'])

                 # FF button
                if tracks and ui.btn_ff.collidepoint(p):
                    # trigger UI anim
                    state['btn_pressed'] = "ff"

                    # add FAST_FORWARD_DUR to current pos
                    new_pos = min(state['pos_s'] + FAST_FORWARD_DUR, state['dur'])

                    # if ff'd past clip duration while repeat is on
                    if new_pos >= state['dur'] and state['repeat']:
                        # load same track
                        load_track(tracks, state, state['track_idx'])
                    else:
                        state['pos_s'] = new_pos
                        pygame.mixer.music.play(start=new_pos)

                 # REV button
                if tracks and ui.btn_rev.collidepoint(p):
                    # trigger UI anim
                    state['btn_pressed'] = "rev"

                    # sub REV_DUR from current pos
                    new_pos = max(state['pos_s'] - REV_DUR, 0.0)

                    # if rev'd past clip duration while repeat is on
                    if new_pos <= 0 and state['repeat']:
                        # load same track
                        load_track(tracks, state, state['track_idx'])
                    else:
                        state['pos_s'] = new_pos
                        pygame.mixer.music.play(start=new_pos)

                # Shuffle button
                elif ui.btn_shf.collidepoint(p):
                    state['shuffle'] = not state['shuffle']

                # Repeat button
                elif ui.btn_rpt.collidepoint(p):
                    state['repeat'] = not state['repeat']

                # Next button
                elif ui.btn_next.collidepoint(p):
                    # UI anim
                    state['btn_pressed'] = "next"
                    next_track(tracks,state)

                # Prev button
                elif ui.btn_prev.collidepoint(p):
                    # UI anim
                    state['btn_pressed'] = "prev"
                    prev_track(tracks,state)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # clear UI anim state
                state['btn_pressed'] = None


        if state['is_playing']:
            pygame.mixer.music.unpause()
            state['wave_t'] += dt

            # get_pos() returns ms since track started playing as int
            cur_playback_ms = pygame.mixer.music.get_pos()

            # returns -1 if no music is playing, hence guard
            if cur_playback_ms >= 0:
                state['pos_s'] = min(state['pos_s'] + dt, state['dur'])
            # ties it to framerate

            # 40 px/sec title scroll
            state['scroll_x'] = state.get('scroll_x', 0.0) + dt * TITLE_SCROLL_SPEED

            # auto advance when current position greater than track length
            if state['pos_s'] >= state['dur']:
                next_track(tracks, state)
                state['scroll_x'] = 0

        else:
            pygame.mixer.music.pause()


        ui.draw_frame(screen, fonts, state)

        if fb_device is not None:
            display_driver.push(screen, fb_device)
        else:
            pygame.display.flip()

except KeyboardInterrupt:
    print("\nExiting OpenPiAmp...")

if fb_device is not None:
    fb_device.close()

    # Force console driver (fbcon) to redraw tty1 over it by sending a terminal
    # reset sequence straight to the vt mapped onto this screen.
    try:
        with open("/dev/tty1", "w") as tty1:
            tty1.write("\033c")
    except OSError as e:
        print(f"(couldn't repaint console on exit: {e})")

pygame.quit()
