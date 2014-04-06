import pygame

from gslib.constants import *


class KeyController(object):
    def __init__(self, game):
        self.game = game

    def handle_keys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.game.keys:
                self.game.keys[event.key] = True
        if event.type == pygame.KEYUP:
            if event.key in self.game.keys:
                self.game.keys[event.key] = False

        if self.game.keys[pygame.K_ESCAPE] and self.game.GameState != CUTSCENE:
            self.game.keys[pygame.K_ESCAPE] = False
            self.game.GameState = MAIN_MENU
        if self.game.keys[pygame.K_m]:
            self.game.keys[pygame.K_m] = False
            if self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME:
                self.game.GameState = CUTSCENE
        if self.game.keys[pygame.K_s] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.GameState = SKILLS_SCREEN
        if self.game.keys[pygame.K_t] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.GameState = TEXTBOX_TEST