import pygame

def getRect(left, top, width, height):
    if left >= 0 and top >= 0 and width > 0 and height > 0:
        return pygame.Rect(left, top, width, height)
    else:
        return None

