import pygame

from gslib import character
from gslib.constants import *


class JoyController(object):
    def __init__(self, game):
        self.game = game

        if not pygame.joystick.get_init():
            pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            pygame.joystick.quit()
            return
        else:
            self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            for joystick in self.joysticks:
                joystick.init()

    def handle_hat(self, event):
        x, y = event.value
        if x == -1:
            self.game.players[0].move_left = True
        elif x == 1:
            self.game.players[0].move_right = True
        elif x == 0:
            self.game.players[0].move_left = False
            self.game.players[0].move_right = False
        if y == -1:
            self.game.players[0].move_down = True
        elif y == 1:
            self.game.players[0].move_up = True
        elif y == 0:
            self.game.players[0].move_down = False
            self.game.players[0].move_up = False

    def handle_buttondown(self, event):
        if event.button == 0:
            self.game.objects.append(
                character.Character(self.game, self.game.player1.coord[0], self.game.player1.coord[1], 16, 16,
                                    character.gen_character()))
        elif event.button == 1:
            if self.game.GameState == MAIN_MENU:
                self.game.set_state(MAIN_GAME)
            elif self.game.GameState == MAIN_GAME or self.game.GameState == GAME_OVER:
                self.game.set_state(MAIN_MENU)
        elif event.button == 2:
            self.game.options['FOV'] = not self.game.options['FOV']
        elif event.button == 3:
            self.game.options['VOF'] = not self.game.options['VOF']
        elif event.button == 4:
            self.game.options['torch'] = not self.game.options['torch']

    def handle_buttonup(self, event):
        pass

    def handle_axis(self, event):
        if event.axis == 0:
            if event.value < -0.1:
                self.game.players[0].move_left = True
            elif event.value > 0.1:
                self.game.players[0].move_right = True
            else:
                self.game.players[0].move_left = False
                self.game.players[0].move_right = False
        elif event.axis == 1:
            if event.value < -0.1:
                self.game.players[0].move_up = True
            elif event.value > 0.1:
                self.game.players[0].move_down = True
            else:
                self.game.players[0].move_down = False
                self.game.players[0].move_up = False

    def handle_ball(self, event):
        self.handle_axis(event)
