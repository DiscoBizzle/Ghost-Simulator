import pygame

from gslib import button
from gslib.constants import *


class MainMenu(object):
    def __init__(self, GameClass):
        self.GameClass = GameClass
        self.buttons = {}
        self.buttons['main_game'] = button.Button(self, self.goto_main_game, pos=(60, 40), size=(200, 30), visible=True,
                                                  text='Start Game', border_colour=(120, 50, 80), border_width=3,
                                                  colour=(120, 0, 0))
        self.buttons['FOV'] = button.Button(self, self.FOV_toggle, pos=(60, 80), size=(200, 30), visible=True,
                                            text='Field of View: Yes', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['VOF'] = button.Button(self, self.VOF_toggle, pos=(60, 120), size=(200, 30), visible=True,
                                            text='View of Field: No', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['quit'] = button.Button(self, self.quit, pos=(60, 240), size=(200, 30), visible=True, text='Quit',
                                             border_colour=(120, 50, 80), border_width=3,
                                             colour=(120, 0, 0))

    def display(self):
        # self.GameClass.surface.fill((0, 0, 0))
        for button in self.buttons.itervalues():
            self.GameClass.surface.blit(button.surface, button.pos) # self.buttons[button]

        # pygame.display.update()

    def mouse_event(self, event):
        for button in self.buttons.itervalues():
            button.check_clicked(event.pos)

    def goto_main_game(self):
        self.GameClass.GameState = MAIN_GAME

    def FOV_toggle(self):
        if self.GameClass.options['FOV']:
            self.GameClass.options['FOV'] = False
            self.buttons['FOV'].text = 'Field of View: No'
        else:
            self.GameClass.options['FOV'] = True
            self.buttons['FOV'].text = 'Field of View: Yes'

    def VOF_toggle(self):
        if self.GameClass.options['VOF']:
            self.GameClass.options['VOF'] = False
            self.buttons['VOF'].text = 'View of Field: No'
        else:
            self.GameClass.options['VOF'] = True
            self.buttons['VOF'].text = 'View of Field: Yes'

    def quit(self):
        self.GameClass.gameRunning = False


class OptionsMenu(object):
    def __init__(self, GameClass):
        self.GameClass = GameClass
        self.buttons = {}
