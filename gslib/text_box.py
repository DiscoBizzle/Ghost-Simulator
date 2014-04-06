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
        self.bg_color = pygame.Color((125, 25, 32))
        self.x_pad = 16
        self.y_pad = 16
        self.h = 256
        self.portrait = pygame.image.load("characters/portrait_test.png")

        self.state = INACTIVE
        self.coord = (self.x_pad, GAME_HEIGHT - self.h - self.y_pad)
        self.base_rect = pygame.Rect(0, 0, GAME_WIDTH - 2*self.x_pad, self.h)
        self.portrait_rect = pygame.Rect(16, 16, self.h-32, self.h-32)

    def create_background_surface(self): # creates a surface for the textbox (minus the text so we can make that scroll)
        self.background_surface = pygame.Surface(self.base_rect.w, self.base_rect.h)
        self.background_surface.fill(self.bg_color)

        pass

