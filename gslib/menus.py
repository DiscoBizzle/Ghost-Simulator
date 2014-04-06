import pygame

from gslib import button
from gslib import slider
from gslib.constants import *


class Menu(object):
    def __init__(self, game_class):
        self.game_class = game_class
        self.buttons = {}
        self.sliders = {}

    def display(self):
        for button in self.buttons.itervalues():
            self.game_class.graphics.surface.blit(button.surface, button.pos)
        for slider in self.sliders.itervalues():
            self.game_class.graphics.surface.blit(slider.surface, slider.pos)

    def mouse_event(self, event):
        for slider in self.sliders.itervalues():
            slider.check_clicked(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons.itervalues():
                button.check_clicked(event.pos)

    def arrange_buttons(self):
        for button in self.buttons.itervalues():
            button.pos = (60, 40 + button.order*40)


class MainMenu(Menu):
    def __init__(self, game_class):
        Menu.__init__(self, game_class)
        self.buttons['main_game'] = button.Button(self, self.go_to_main_game, order = 0, size=(200, 30), visible=True,
                                                  text=u'Start Game', border_colour=(120, 50, 80), border_width=3,
                                                  colour=(120, 0, 0))
        self.buttons['credits'] = button.Button(self, self.credits, order = 1, size=(200, 30), visible=True, text=u'Credits',
                                             border_colour=(120, 50, 80), border_width=3,
                                             colour=(120, 0, 0))
        self.buttons['quit'] = button.Button(self, self.game_class.quit_game, order = 3, size=(200, 30), visible=True, text=u'Quit',
                                             border_colour=(120, 50, 80), border_width=3,
                                             colour=(120, 0, 0))
        self.buttons['options'] = button.Button(self, self.go_to_options, order = 2, size=(200, 30), visible=True, text=u'Options',
                                             border_colour=(120, 50, 80), border_width=3,
                                             colour=(120, 0, 0))

        Menu.arrange_buttons(self)

    def go_to_main_game(self):
        self.game_class.GameState = MAIN_GAME

    def go_to_options(self):
        self.game_class.GameState = OPTIONS_MENU

    def credits(self):
        self.game_class.GameState = CREDITS


class OptionsMenu(Menu):
    def __init__(self, game_class):
        Menu.__init__(self, game_class)
        self.buttons['FOV'] = button.Button(self, self.FOV_toggle, order = 0, size=(200, 30), visible=True,
                                            text=u'Field of View: Yes', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['VOF'] = button.Button(self, self.VOF_toggle, order = 1, size=(200, 30), visible=True,
                                            text=u'View of Field: No', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['torch'] = button.Button(self, self.torch_toggle, order = 2, size=(200, 30), visible=True,
                                            text=u'Torch: Yes', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['sound_volume_up'] = button.Button(self, self.sound_up, order = 3, size=(200, 30), visible=True,
                                            text=u'Increase Sound Volume', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['sound_volume_down'] = button.Button(self, self.sound_down, order = 4, size=(200, 30), visible=True,
                                            text=u'Decrease Sound Volume', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))

        self.sliders['sound'] = slider.Slider(self, self.set_sound, range=(0, 1))
        Menu.arrange_buttons(self)

    def FOV_toggle(self):
        if self.game_class.options['FOV']:
            self.game_class.options['FOV'] = False
            self.buttons['FOV'].text = u'Field of View: No'
        else:
            self.game_class.options['FOV'] = True
            self.buttons['FOV'].text = u'Field of View: Yes'

    def VOF_toggle(self):
        if self.game_class.options['VOF']:
            self.game_class.options['VOF'] = False
            self.buttons['VOF'].text = u'View of Field: No'
        else:
            self.game_class.options['VOF'] = True
            self.buttons['VOF'].text = u'View of Field: Yes'

    def torch_toggle(self):
        if self.game_class.options['torch']:
            self.game_class.options['torch'] = False
            self.buttons['torch'].text = u'Torch: No'
        else:
            self.game_class.options['torch'] = True
            self.buttons['torch'].text = u'Torch: Yes'

    def set_sound(self, value):
        for sound in self.game_class.sound_dict.itervalues():
            sound.set_volume(value)

    def sound_up(self):
        for sound in self.game_class.sound_dict.itervalues():
            if sound.get_volume != 1:
                sound.set_volume(sound.get_volume()+0.1)

    def sound_down(self):
        for sound in self.game_class.sound_dict.itervalues():
            if sound.get_volume != 0:
                sound.set_volume(sound.get_volume()-0.1)


class SkillsMenu(object):
    def __init__(self, game_class):
        self.game_class = game_class
        self.buttons = {}
        x_offset = 0
        y_offset = 0
        for skill in self.game_class.skills_dict:
            if skill in self.game_class.player1.skills_learnt:
                skill_colour = LEARNT_SKILL_COLOUR
            elif self.game_class.skills_dict[skill].can_be_learnt(self.game_class.player1):
                skill_colour = CAN_BE_LEARNT_COLOUR
            else:
                skill_colour = UNLEARNABLE_COLOUR
            f = lambda skill=skill: self.learn_skill(skill)
            self.buttons[skill] = button.Button(self, f, pos = (60 + x_offset, 40 + y_offset),
                                                size = (200, 150), text = skill, border_colour = (120, 50, 80),
                                                border_width = 3, colour = skill_colour)
            if x_offset < GAME_WIDTH - 420:
                x_offset += 220
            else:
                x_offset = 0
                y_offset += 170

    def display(self):
        for button in self.buttons.itervalues():
            self.game_class.graphics.surface.blit(button.surface, button.pos)

    def mouse_event(self, event):
        for button in self.buttons.itervalues():
            button.check_clicked(event.pos)

    def learn_skill(self, skill):
        self.game_class.player1.learn_skill(skill)
        print self.game_class.player1.skills_learnt

        for skill in self.buttons:
            if skill in self.game_class.player1.skills_learnt:
                skill_colour = LEARNT_SKILL_COLOUR
            elif self.game_class.skills_dict[skill].can_be_learnt(self.game_class.player1):
                skill_colour = CAN_BE_LEARNT_COLOUR
            else:
                skill_colour = UNLEARNABLE_COLOUR
            self.buttons[skill].colour = skill_colour
