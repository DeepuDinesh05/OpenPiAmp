import pygame
import ui

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

state = {
    'wave_t':      0.0,
    'track_name':  "Example",
    'pos_s':       2.0,
    'dur':         265.0,
    'volume':      0.7,
    'track_idx':   0,
    'track_count': 2,
    'is_playing':  True,
    'shuffle':     False,
    'repeat':      False,
}

running = True
while running:
    dt = clock.tick(30) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                running = False
            elif event.key == pygame.K_SPACE:
                state['is_playing'] = not state['is_playing']
            elif event.key == pygame.K_F1:
                state['shuffle'] = not state['shuffle']
            elif event.key == pygame.K_F2:
                state['repeat'] = not state['repeat']

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            p = event.pos
            if ui.btn_play.collidepoint(p):
                state['is_playing'] = not state['is_playing']
            elif ui.btn_shf.collidepoint(p):
                state['shuffle'] = not state['shuffle']
            elif ui.btn_rpt.collidepoint(p):
                state['repeat'] = not state['repeat']

    if state['is_playing']:
        state['wave_t'] += dt
        state['pos_s'] = min(state['pos_s'] + dt, state['dur'])

    ui.draw_frame(screen, fonts, state)

pygame.quit()
