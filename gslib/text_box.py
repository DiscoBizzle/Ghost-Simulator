import pygame
from gslib.constants import *
from gslib import text

#define a list of textbox states

class TextBox:
    def __init__(self, game, text, on_complete_fun):
        self.game = game
        self.on_complete_fun = on_complete_fun

        self.bg_color = pygame.Color(125, 25, 32)
        self.text_frame_color = pygame.Color(0, 0, 0)
        self.text_color = pygame.Color(150, 255, 150)
        self.font = pygame.font.SysFont(FONT, 16)
        self.text = text

        self.x_ext_pad = 16
        self.y_ext_pad = 16
        self.x_int_pad = 16
        self.y_int_pad = 16
        self.x_text_pad = 16
        self.y_text_pad = 16
        self.line_space = 2

        self.num_chars = 1
        self.char_increment = 2
        self.tick = 0  # counts the number of ticks since textbox appeared

        self.h = 160
        self.w = GAME_WIDTH - 2*self.x_int_pad

        self.draw_rect = pygame.Rect(0, 0, self.w, 0)

        self.portrait_surface = pygame.image.load("characters/portrait_test2.jpg").convert()
        self.background_surface = pygame.Surface((int(self.w), int(self.h)))  # create surface

        self.state = TB_INACTIVE

        self.coord = (self.x_ext_pad, GAME_HEIGHT - self.h - self.y_ext_pad)
        self.base_rect = pygame.Rect(self.x_ext_pad, self.y_ext_pad, self.w, self.h)
        self.portrait_rect = pygame.Rect(self.x_int_pad, (self.h/2 - self.portrait_surface.get_height()/2),
                                         self.portrait_surface.get_width(), self.portrait_surface.get_height())

        self.text_frame_rect = pygame.Rect(
            2*self.x_int_pad + self.portrait_rect.w, self.y_int_pad,
            self.w - 3*self.x_int_pad - self.portrait_rect.w, self.h - 2*self.y_int_pad)

        self.text_surface = pygame.Surface((self.text_frame_rect.w, self.text_frame_rect.h))

    def show(self):
        # ??? start text box
        self.game.text_box = self
        # TODO: update key.py etc to pass input only to game.text_box if game.text_box is not None
        pass

    def hide(self):
        # ??? stop text box. usually should be called by text_box itself when convo is finished
        self.game.text_box = None

        # blah blah blah

        if self.on_complete_fun is not None:
            self.on_complete_fun(some_info_about_dialogue_branch_chosen)

    def draw(self):
        # add sprites/buttons to end of self.game.screen_objects_to_draw list
        # self.game.screen_objects_to_draw += [thing1, thing2, etc]
        pass

    def create_background_surface(self):  # creates a surface for the textbox (minus the text so we can make that scroll)
        self.background_surface.fill(self.bg_color)  # fill background
        self.background_surface.blit(self.portrait_surface, self.portrait_rect)  # blit portrait
        pygame.draw.rect(self.background_surface, self.text_frame_color, self.text_frame_rect)  # fill text background

    def create_text_surface(self):
        current_text = self.text[:self.num_chars]
        self.text_surface.fill(self.text_frame_color)
        lines = text.text_wrap(current_text, self.font, self.text_frame_rect.w - self.x_text_pad*2)
        t = self.font.render(lines[0], True, self.text_color)
        for i, l in enumerate(lines):
            t = self.font.render(l, True, self.text_color)
            self.text_surface.blit(t, (self.x_text_pad, self.y_text_pad + i * (t.get_height()+self.line_space)))

            self.tick += 1
            if self.tick % TICKS_PER_CHAR == 0:
                self.num_chars += self.char_increment

    def update(self):
        if self.state == TB_INACTIVE:
            #wait for trigger
            pass
        elif self.state == TB_STARTING:
            self.draw_rect.h += TB_OPEN_SPEED
            if self.draw_rect.h >= self.h:
                self.draw_rect.h = self.h
                self.state = TB_WRITING
        elif self.state == TB_WRITING:
            self.create_text_surface()
            if self.num_chars >= len(self.text):
                self.num_chars = len(self.text)
                self.state = TB_ACTIVE
        elif self.state == TB_ACTIVE:
            #wait for button input
            self.state = TB_CLOSING
            self.num_chars = 0
            self.create_text_surface()
            pass
        elif self.state == TB_CLOSING:
            self.draw_rect.h -= TB_OPEN_SPEED
            if self.draw_rect.h <= 0:
                self.draw_rect.h = 0
                self.state = TB_INACTIVE

