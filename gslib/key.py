import pygame

from gslib.constants import *


class KeyController(object):
    def __init__(self, game):
        self.game = game

        self.keys = {pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False,
                     pygame.K_ESCAPE: False, pygame.K_m: False, pygame.K_s: False, pygame.K_t: False}

    def handle_keys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.keys:
                self.keys[event.key] = True
        if event.type == pygame.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = False

        if self.keys[pygame.K_ESCAPE] and self.game.GameState != CUTSCENE:
            self.keys[pygame.K_ESCAPE] = False
            self.game.GameState = MAIN_MENU
        if self.keys[pygame.K_m]:
            self.keys[pygame.K_m] = False
            if self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME:
                self.game.GameState = CUTSCENE
        if self.keys[pygame.K_s] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.GameState = SKILLS_SCREEN
        if self.keys[pygame.K_t] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.GameState = TEXTBOX_TEST

        self.game.player1.move_down = self.keys[pygame.K_DOWN]
        self.game.player1.move_up = self.keys[pygame.K_UP]
        self.game.player1.move_left = self.keys[pygame.K_LEFT]
        self.game.player1.move_right = self.keys[pygame.K_RIGHT]
