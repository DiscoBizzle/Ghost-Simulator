import pygame

from gslib.constants import *


class KeyController(object):
    def __init__(self, game):
        self.game = game

        self.keys = {pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False,
                     pygame.K_ESCAPE: False, pygame.K_m: False, pygame.K_q: False, pygame.K_t: False,
                     pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False, pygame.K_e: False}

        self.player_map = {0: {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT},
                           1: {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d}}

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
        if self.keys[pygame.K_q] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.GameState = SKILLS_SCREEN
        if self.keys[pygame.K_t] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.GameState = TEXTBOX_TEST

        if self.game.GameState == MAIN_GAME:
            self.game.show_fears = self.keys[pygame.K_e]

        for i, p in enumerate(self.game.players):
            p.move_down = self.keys[self.player_map[i]['down']]
            p.move_up = self.keys[self.player_map[i]['up']]
            p.move_left = self.keys[self.player_map[i]['left']]
            p.move_right = self.keys[self.player_map[i]['right']]
