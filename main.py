import pygame
from modules.settings import *
# pygame setup
pygame.font.init()
my_font = pygame.font.Font("Kavoon-Regular.ttf", 40)
screen = pygame.display.set_mode((1280, 720))
pygame.init()
screensize = (1280, 720)
screen = pygame.display.set_mode(screensize)
clock = pygame.time.Clock()
pcb_rect = pygame.Rect(1280/9, 729/3, 300, 300)
pcb_image = pygame.image.load("pcb.jpg")
pcb_image = pygame.transform.scale(pcb_image, (300, 300))
settings_image = pygame.image.load('Settings.png')
settings_image = pygame.transform.scale(settings_image, (50, 50))
settings_rect = pygame.Rect(1200, 40, 50, 50)
running = True
pcb = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            if pcb_rect.collidepoint(event.pos):
                pcb += 1
            pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            running = False

    screen.fill("#B2EAD3")
    screen.blit(pcb_image, pcb_rect)
    screen.blit(settings_image, settings_rect)

    # RENDER YOUR GAME HERE
    text_surface = my_font.render(f"{pcb} PCBs", True, (255, 255, 255))
    screen.blit(text_surface, (100, 50))


    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(15)  # limits FPS to 30

pygame.quit()