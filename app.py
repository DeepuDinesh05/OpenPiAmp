import pygame

import ui
from config import *
from music_loader import *


pygame.init()
pygame.display.set_caption("OpenPiAmp")

fonts = {
    'f_title': pygame.font.Font(None, 22),
    'f_time':  pygame.font.Font(None, 16),
    'f_btn':   pygame.font.Font(None, 20),
    'f_small': pygame.font.Font(None, 15),
}

screen = pygame.display.set_mode((ui.W, ui.H))
clock  = pygame.time.Clock()

# init default state
state = {
    'wave_t':      0.0,
    'track_name':  "-",
    'pos_s':       2.0,
    'dur':         265.0,
    'volume':      0.7,
    'track_idx':   0,
    'track_count': 0,
    'is_playing':  True,
    'shuffle':     False,
    'repeat':      False,
    'scroll_x' : 0
}

# scan music directory and init state with actual music data
tracks = scan(MUSIC_DIR,state)

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse button support only, to be translated into touch input
        # Have to finalize driver support
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            p = event.pos
            if ui.btn_play.collidepoint(p):
                state['is_playing'] = not state['is_playing']
                # print(state['is_playing'])
            
            elif ui.btn_shf.collidepoint(p):
                state['shuffle'] = not state['shuffle']
            
            elif ui.btn_rpt.collidepoint(p):
                state['repeat'] = not state['repeat']

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
    
    else:
        pygame.mixer.music.pause()


    ui.draw_frame(screen, fonts, state)

pygame.quit()
