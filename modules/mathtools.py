import pygame



def ptc(percent: tuple, customsize=None):

    percentx, percenty = percent
    screen = pygame.display.get_surface()
    screenx, screeny = (screen.get_width(), screen.get_height())
    if customsize:
        screenx, screeny = customsize
    posx = int((screenx/100)*percentx)
    posy = int((screeny/100)*percenty)
    return posx, posy

def ptw(percent: int, width: int):
    return int(width / 100)*percent

def ptcx(percentx):
    w, h = pygame.display.get_surface().get_size()
    x = percentx/100*w
    return int(x)

def ptcy(percenty):
    w, h = pygame.display.get_surface().get_size()
    y = percenty/100*h
    return int(y)