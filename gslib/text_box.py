import pygame

from gslib.constants import *
import text_functions

#define a list of textbox states
INACTIVE = 0
STARTING = 1
WRITING = 2
ACTIVE = 3
CLOSING = 4


class TextBox:
    def __init__(self, text):
        self.bg_color = pygame.Color(125, 25, 32)
        self.text_frame_color = pygame.Color(0, 0, 0)
        self.text_color = pygame.Color(150,255,150)
        self.font = pygame.font.SysFont('helvetica', 16)
        self.text = text

        self.x_ext_pad = 16
        self.y_ext_pad = 16
        self.x_int_pad = 16
        self.y_int_pad = 16
        self.x_text_pad = 16
        self.y_text_pad = 16
        self.line_space = 2

        self.num_chars = 1

        self.h = 224
        self.w = GAME_WIDTH - 2*self.x_int_pad

        self.portrait_surface = pygame.image.load("characters/portrait_test2.jpg").convert()
        self.background_surface = pygame.Surface((int(self.w), int(self.h)))  # create surface

        self.state = INACTIVE

        self.coord = (self.x_ext_pad, GAME_HEIGHT - self.h - self.y_ext_pad)
        self.base_rect = pygame.Rect(0, 0, self.w, self.h)
        self.portrait_rect = pygame.Rect(self.x_int_pad, (self.h/2 - self.portrait_surface.get_height()/2),
                                         self.portrait_surface.get_width(), self.portrait_surface.get_height())

        self.text_frame_rect = pygame.Rect(
            2*self.x_int_pad + self.portrait_rect.w, self.y_int_pad,
            self.w - 3*self.x_int_pad - self.portrait_rect.w, self.h - 2*self.y_int_pad)

        self.text_surface = pygame.Surface((self.text_frame_rect.w,self.text_frame_rect.h))

    def create_background_surface(self):  # creates a surface for the textbox (minus the text so we can make that scroll)
        self.background_surface.fill(self.bg_color)  # fill background
        self.background_surface.blit(self.portrait_surface, self.portrait_rect)  # blit portrait
        pygame.draw.rect(self.background_surface, self.text_frame_color, self.text_frame_rect)  # fill text background

    def create_text_surface(self):
        current_text = self.text[:self.num_chars]
        self.text_surface.fill(self.text_frame_color)
        lines = text_functions.text_wrap(current_text, self.font, self.text_frame_rect.w - self.x_text_pad*2)
        t = self.font.render(lines[0], True, self.text_color)
        for i, l in enumerate(lines):
            t = self.font.render(l, True, self.text_color)
            self.text_surface.blit(t, (self.x_text_pad, self.y_text_pad + i * (t.get_height()+self.line_space)))
        self.num_chars += 1
