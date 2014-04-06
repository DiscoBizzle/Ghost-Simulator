from constants import *
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
        self.h = 256

        self.state = INACTIVE
        self.coord = (self.x_pad, GAME_HEIGHT - self.h - self.y_pad)
        self.base_rect = pygame.Rect(0, 0, GAME_WIDTH - 2*self.x_pad, self.h)

    def create_background_surface(self): # creates a surface for the textbox (minus the text so we can make that scroll)
        #self.background_surface =
        pass

