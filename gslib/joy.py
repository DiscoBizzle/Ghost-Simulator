from pyglet import input

from gslib import character
from gslib.constants import *


class JoyController(object):
    def __init__(self, game):
        self.game = game

        self.joysticks = input.get_joysticks()
        for joystick in self.joysticks:
            joystick.open()
            joystick.push_handlers(self)

    def on_joyaxis_motion(self, joystick, axis, value):
        player1 = self.game.players['player1']
        player2 = self.game.players['player2']
        if axis == 'x':
            player1.move_left = value < -0.1
            player1.move_right = value > 0.1
        elif axis == 'y':
            player1.move_up = value < -0.1
            player1.move_down = value > 0.1
        if axis == 'rz':
            player2.move_left = value < -0.1
            player2.move_right = value > 0.1
        elif axis == 'z':
            player2.move_up = value < -0.1
            player2.move_down = value > 0.1

    def on_joybutton_press(self, joystick, button):
        if button == 0:
            self.game.players['player1'].harvest_fear()
        elif button == 1:
            self.game.players['player1'].toggle_possess()
        elif button == 2:
            self.game.show_fears = not self.game.show_fears
        elif button == 3:
            self.game.show_ranges = not self.game.show_ranges
        elif button == 4:
            self.game.options['FOV'] = not self.game.options['FOV']
        elif button == 5:
            self.game.options['VOF'] = not self.game.options['VOF']
        elif button == 6:
            self.game.options['torch'] = not self.game.options['torch']
        elif button == 9:
            if self.game.GameState == MAIN_MENU:
                self.game.set_state(MAIN_GAME)
            elif self.game.GameState == MAIN_GAME or self.game.GameState == GAME_OVER:
                self.game.set_state(MAIN_MENU)

    def on_joybutton_release(self, joystick, button):
        pass

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        player = self.game.players['player1']
        player.move_left = hat_x == -1
        player.move_right = hat_x == 1
        player.move_down = hat_y == -1
        player.move_up = hat_y == 1
