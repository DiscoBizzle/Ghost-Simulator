from pyglet import input

from gslib import character
from gslib.constants import *


class JoyController(object):
    def __init__(self, game):
        self.game = game

        self.joysticks = input.get_joysticks()
        for joystick in self.joysticks:
            joystick.open()
            joystick.set_handler('on_joyaxis_motion', self.on_joyaxis_motion)
            joystick.set_handler('on_joybutton_press', self.on_joybutton_press)
            joystick.set_handler('on_joybutton_release', self.on_joybutton_release)
            joystick.set_handler('on_joyhat_motion', self.on_joyhat_motion)

    def on_joyaxis_motion(self, joystick, axis, value):
        if axis == 'x':
            if value < -0.1:
                self.game.players['player1'].move_left = True
            elif value > 0.1:
                self.game.players['player1'].move_right = True
            else:
                self.game.players['player1'].move_left = False
                self.game.players['player1'].move_right = False
        elif axis == 'y':
            if value < -0.1:
                self.game.players['player1'].move_up = True
            elif value > 0.1:
                self.game.players['player1'].move_down = True
            else:
                self.game.players['player1'].move_down = False
                self.game.players['player1'].move_up = False

    def on_joybutton_press(self, joystick, button):
        if button == 0:
            self.game.objects['testguy'] = character.Character(self.game, self.game.players['player1'].coord[0],
                                                               self.game.players['player1'].coord[1], 16, 16,
                                                               character.gen_character())
        elif button == 1:
            if self.game.GameState == MAIN_MENU:
                self.game.set_state(MAIN_GAME)
            elif self.game.GameState == MAIN_GAME or self.game.GameState == GAME_OVER:
                self.game.set_state(MAIN_MENU)
        elif button == 2:
            self.game.options['FOV'] = not self.game.options['FOV']
        elif button == 3:
            self.game.options['VOF'] = not self.game.options['VOF']
        elif button == 4:
            self.game.options['torch'] = not self.game.options['torch']

    def on_joybutton_release(self, joystick, button):
        pass

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        if hat_x == -1:
            self.game.players['player1'].move_left = True
        elif hat_x == 1:
            self.game.players['player1'].move_right = True
        elif hat_x == 0:
            self.game.players['player1'].move_left = False
            self.game.players['player1'].move_right = False
        if hat_y == -1:
            self.game.players['player1'].move_down = True
        elif hat_y == 1:
            self.game.players['player1'].move_up = True
        elif hat_y == 0:
            self.game.players['player1'].move_down = False
            self.game.players['player1'].move_up = False
