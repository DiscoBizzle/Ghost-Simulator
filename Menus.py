import Button
import pygame
from Constants import *


class MainMenu(object):
    def __init__(self, GameClass):
        self.GameClass = GameClass
        self.buttons = {}
        self.buttons['Ball'] = Button.Button(self, 'goto_ball()', pos=(60, 40), size=(100, 30), visible=True, text='BALL')

    def display(self):
        self.GameClass.surface.fill((0, 0, 0))
        for button in self.buttons.itervalues():
            self.GameClass.surface.blit(button.surface, button.pos) # self.buttons[button]

        pygame.display.update()

    def mouse_event(self, event):
        for button in self.buttons.itervalues():
            button.check_clicked(event.pos)

    def goto_ball(self):
        self.GameClass.GameState = MAIN_GAME


class OptionsMenu(object):
    def __init__(self, GameClass):
        self.GameClas = GameClass
        self.buttons = {}