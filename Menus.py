import Button
import pygame
from Constants import *


class MainMenu(object):
    def __init__(self, GameClass):
        self.GameClass = GameClass
        self.buttons = {}
        self.buttons['Ball'] = Button.Button(self, 'goto_ball()', pos=(60, 40), size=(100, 30), visible=True, text='BALL')
        self.buttons['FOV'] = Button.Button(self, 'FOV_toggle()', pos=(60, 80), size=(200, 30), visible=True, text='Field of View: Yes')
        self.buttons['VOF'] = Button.Button(self, 'VOF_toggle()', pos=(60, 120), size=(200, 30), visible=True, text='View of Field: No')

    def display(self):
        # self.GameClass.surface.fill((0, 0, 0))
        for button in self.buttons.itervalues():
            self.GameClass.surface.blit(button.surface, button.pos) # self.buttons[button]

        # pygame.display.update()

    def mouse_event(self, event):
        for button in self.buttons.itervalues():
            button.check_clicked(event.pos)

    def goto_ball(self):
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



class OptionsMenu(object):
    def __init__(self, GameClass):
        self.GameClas = GameClass
        self.buttons = {}