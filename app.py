import pygame

pygame.init()

SCREEN_W, SCREEN_H = 240, 320

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock  = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
            running = False

    screen.fill((255, 255, 255))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
