import pygame

#define a list of textbox states
INACTIVE = 0
STARTING = 1
WRITING = 2
ACTIVE = 3
CLOSING = 4

class TextBox:
    def __init__(self, text):
        self.x_pad = 16
        self.y_pad = 16
        

        self.state = INACTIVE
        self.base_rect = pygame.Rect()

