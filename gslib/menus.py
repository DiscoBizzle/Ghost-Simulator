import pygame

from gslib import button
from gslib import slider
from gslib.constants import *


class Menu(object):
    def __init__(self, game_class, button_size):
        self.game_class = game_class
        self.buttons = {}
        self.sliders = {}
        self.button_size = button_size
        self.original_button_size = button_size
        mi = min(button_size[0], button_size[1])
        frac = 8.0/mi
        self.frac = frac
        self.min_button_size = (button_size[0] * frac, button_size[1] * frac)
        self.base_font_size = 20
        self.font_size = self.base_font_size
        self.hori_offset = 60
        self.vert_offset = 40 + button_size[1] + 10
        self.buttons_per_column = ((GAME_HEIGHT - self.vert_offset) / (self.button_size[1]+20)) - 1

        self.buttons['menu_scale_display'] = button.Button(self, None, order = (-1, 0), visible=False,
                                            text=u'Menu Scale: 1.0', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0), size=(200, 50), pos=(60, 40))
        self.sliders['menu_scale'] = slider.Slider(self, self.set_menu_scale, range=(1.0, 5.0/frac), order=(-1, 1),
                                                   value=1.0/frac, size=(200, 50), pos=(60 + 200 + 20, 40),
                                                   visible=False, enabled=self.game_class.options['menu_scale'])
        # self.first_time = True

    def display(self):
        if self.game_class.options['menu_scale']:
            self.buttons['menu_scale_display'].visible = True
            self.sliders['menu_scale'].visible = True
            self.sliders['menu_scale'].enabled = True
            self.set_menu_scale(self.sliders['menu_scale'].value)

        else:
            self.buttons['menu_scale_display'].visible = False
            self.sliders['menu_scale'].visible = False
            self.sliders['menu_scale'].enabled = False
            self.set_menu_scale(1.0/self.frac)

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
        self.vert_offset = 50 + self.game_class.options['menu_scale'] * self.buttons['menu_scale_display'].size[1]

        for button in self.buttons.itervalues():
            if button.order[0] == -1:
                continue
            button.size = self.button_size
            button.font_size = self.font_size
            button.pos = (self.hori_offset + (button.order[1] + int(button.order[0]/self.buttons_per_column)*2)*(self.button_size[0]+20), self.vert_offset + (button.order[0]%self.buttons_per_column)*(self.button_size[1]+10))
            if button.text_states:
                button.text = button.text_states[button.text_states_toggle]
        for slider in self.sliders.itervalues():
            if slider.order[0] == -1:
                continue
            slider.size = self.button_size
            slider.pos = (self.hori_offset + (slider.order[1] + int(slider.order[0]/self.buttons_per_column)*2)*(self.button_size[0]+20), self.vert_offset + (slider.order[0]%self.buttons_per_column)*(self.button_size[1]+10))

        # if self.first_time:
        #     self.first_time = False

    def set_menu_scale(self, value):
        self.button_size = (self.min_button_size[0] * value, self.min_button_size[1] * value)
        if self.button_size[0] > GAME_WIDTH - self.hori_offset - 32:
            self.button_size = (GAME_WIDTH - self.hori_offset - 32, self.button_size[1])
        if self.button_size[1] > GAME_HEIGHT - self.vert_offset - 32:
            self.button_size = (self.button_size[0], GAME_HEIGHT - self.vert_offset - 32)

        self.buttons_per_column = int(((GAME_HEIGHT - self.vert_offset) / (self.button_size[1]+20))) #- 1
        self.arrange_buttons()
        self.font_size = int(self.base_font_size * value * self.frac)
        self.buttons['menu_scale_display'].text = u"Menu scale: " + unicode(str(round(self.button_size[0]/self.original_button_size[0],2)))


class MainMenu(Menu):
    def __init__(self, game_class, button_size):
        Menu.__init__(self, game_class, button_size)
        self.buttons['main_game'] = button.Button(self, self.go_to_main_game, order = (0, 0), visible=True,
                                                  text=u'Start Game', border_colour=(120, 50, 80), border_width=3,
                                                  colour=(120, 0, 0))
        self.buttons['credits'] = button.Button(self, self.credits, order = (1, 0), visible=True, text=u'Credits',
                                             border_colour=(120, 50, 80), border_width=2,
                                             colour=(120, 0, 0))
        self.buttons['quit'] = button.Button(self, self.game_class.quit_game, order = (3, 0), visible=True, text=u'Quit',
                                             border_colour=(120, 50, 80), border_width=3,
                                             colour=(120, 0, 0))
        self.buttons['options'] = button.Button(self, self.go_to_options, order = (2, 0), visible=True, text=u'Options',
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
    def __init__(self, game_class, button_size):
        Menu.__init__(self, game_class, button_size)
        self.buttons['FOV'] = button.Button(self, self.FOV_toggle, order = (0, 0), visible=True,
                                            text_states=[u'Field of View: No', u'Field of View: Yes'], border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['VOF'] = button.Button(self, self.VOF_toggle, order = (1, 0), visible=True,
                                            text_states=[u'View of Field: No', u'View of Field: Yes'], border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['torch'] = button.Button(self, self.torch_toggle, order = (2, 0), visible=True,
                                            text_states=[u'Torch: No', u'Torch: Yes'], border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['sound_display'] = button.Button(self, None , order = (3, 0), visible=True,
                                            text=u'Sound Volume: '+unicode(str(int(INITIAL_SOUND_VOLUME/0.003))), border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['music_display'] = button.Button(self, None, order = (4, 0), visible=True,
                                            text=u'Music Volume: '+unicode(str(int(INITIAL_MUSIC_VOLUME/0.003))), border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))

        self.sliders['sound'] = slider.Slider(self, self.set_sound, range=(0, 0.3), order = (3, 1), value = game_class.sound_dict['scream'].get_volume())
        self.sliders['music'] = slider.Slider(self, self.set_music, range=(0, 0.3), order = (4, 1), value = pygame.mixer.music.get_volume())

        self.buttons['menu_scale'] = button.Button(self, self.menu_scale_toggle, order = (5, 0), visible=True,
                                            text_states=[u'Menu Scaling: Off', u'Menu Scaling: On'], border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['key_bind'] = button.Button(self, self.keybind_toggle, order = (6, 0), visible=True,
                                            text=u'Keybind Menu', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['load'] = button.Button(self, self.load, order = (7, 0), visible=True,
                                            text=u'Load Options', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        self.buttons['save'] = button.Button(self, self.save, order = (7, 1), visible=True,
                                            text=u'Save Options', border_colour=(120, 50, 80), border_width=3,
                                            colour=(120, 0, 0))
        Menu.arrange_buttons(self)

    def FOV_toggle(self):
        self.game_class.options['FOV'] = not self.game_class.options['FOV']
        self.buttons['FOV'].text_states_toggle = not self.buttons['FOV'].text_states_toggle

    def VOF_toggle(self):
        self.game_class.options['VOF'] = not self.game_class.options['VOF']
        self.buttons['VOF'].text_states_toggle = not self.buttons['VOF'].text_states_toggle

    def torch_toggle(self):
        self.game_class.options['torch'] = not self.game_class.options['torch']
        self.buttons['torch'].text_states_toggle = not self.buttons['torch'].text_states_toggle

    def keybind_toggle(self):
        self.game_class.GameState = KEYBIND_MENU

    def menu_scale_toggle(self):
        self.game_class.options['menu_scale'] = not self.game_class.options['menu_scale']
        self.buttons['menu_scale'].text_states_toggle = not self.buttons['menu_scale'].text_states_toggle
        self.arrange_buttons()

    def set_sound(self, value):
        self.game_class.options['sound_volume'] = value
        for sound in self.game_class.sound_dict.itervalues():
            sound.set_volume(value)
        self.buttons['sound_display'].text = u'Sound Volume: ' + unicode(str(int(value/0.003)))

    def set_music(self, value):
        self.game_class.options['music_volume'] = value
        pygame.mixer.music.set_volume(value)
        self.buttons['music_display'].text = u'Music Volume: ' + unicode(str(int(value/0.003)))

    def update_button_text_and_slider_values(self):
        self.buttons['FOV'].text_states_toggle = self.game_class.options['FOV']
        self.buttons['VOF'].text_states_toggle = self.game_class.options['VOF']
        self.buttons['torch'].text_states_toggle = self.game_class.options['torch']
        self.buttons['menu_scale'].text_states_toggle = self.game_class.options['menu_scale']

        self.buttons['sound_display'].text = u'Sound Volume: ' + unicode(str(int(self.game_class.options['sound_volume']/0.003)))
        self.buttons['music_display'].text = u'Music Volume: ' + unicode(str(int(self.game_class.options['music_volume']/0.003)))

        self.sliders['sound'].value = self.game_class.options['sound_volume']
        self.sliders['music'].value = self.game_class.options['music_volume']

    def load(self):
        self.game_class.load_options()

    def save(self):
        self.game_class.save_options()


class SkillsMenu(Menu):
    def __init__(self, game_class, button_size):
        Menu.__init__(self, game_class, button_size)
        temp_order = 0
        for skill in self.game_class.skills_dict:
            if skill in self.game_class.player1.skills_learnt:
                skill_colour = LEARNT_SKILL_COLOUR
            elif self.game_class.skills_dict[skill].can_be_learnt(self.game_class.player1):
                skill_colour = CAN_BE_LEARNT_COLOUR
            else:
                skill_colour = UNLEARNABLE_COLOUR
            f = lambda skill2=skill: self.learn_skill(skill2)
            self.buttons[skill] = button.Button(self, f, text = skill + " cost:" + str(self.game_class.skills_dict[skill].cost), border_colour = (120, 50, 80),
                                                border_width = 3, colour = skill_colour, order = (temp_order, 0))
            self.buttons[skill + "_description"] = button.Button(self, None, text = self.game_class.skills_dict[skill].description,
                                                                 border_colour = (120, 50, 80), border_width = 3, colour = (30, 120, 140), order = (temp_order, 1))
            temp_order += 1
        Menu.arrange_buttons(self)

    def learn_skill(self, skill):
        self.game_class.player1.learn_skill(skill)
        print self.game_class.player1.skills_learnt

        for skill in self.buttons:
            if self.buttons[skill].order[0] != -1 and self.buttons[skill].order[1] == 0:
                if skill in self.game_class.player1.skills_learnt:
                    skill_colour = LEARNT_SKILL_COLOUR
                elif self.game_class.skills_dict[skill].can_be_learnt(self.game_class.player1):
                    skill_colour = CAN_BE_LEARNT_COLOUR
                else:
                    skill_colour = UNLEARNABLE_COLOUR
                self.buttons[skill].colour = skill_colour


class KeyBindMenu(Menu):
    def __init__(self, game_class, button_size):
        Menu.__init__(self, game_class, button_size)
        self.border_colour = (120, 50, 80)
        self.colour = (120, 0, 0)

        self.active_border_colour = (50, 120, 80)
        self.active_colour = (0, 120, 0)

        self.create_buttons()

    def create_buttons(self):
        ord = 0
        self.buttons['load'] = button.Button(self, self.load, order=(ord, 0), visible=True, text=unicode('Load'),
                                             border_colour=self.border_colour, border_width=3,
                                             colour=self.colour)
        self.buttons['save'] = button.Button(self, self.save, order=(ord, 1), visible=True, text=unicode('Save'),
                                             border_colour=self.border_colour, border_width=3,
                                             colour=self.colour)
        ord += 1
        for player, p_map in self.game_class.key_controller.player_map.iteritems():
            for k, v in p_map.iteritems():
                name = 'Player ' + str(player) + ' ' + k
                self.buttons[name] = button.Button(self, None, order=(ord, 0), visible=True, text=unicode(name),
                                                   border_colour=self.border_colour, border_width=3,
                                                   colour=self.colour)
                self.buttons[name + ' key'] = button.Button(self, self.rebind(name), order=(ord, 1), visible=True, text=unicode(pygame.key.name(p_map[k])),
                                                            border_colour=self.border_colour, border_width=3,
                                                            colour=self.colour)
                ord += 1

        for k, v in self.game_class.key_controller.key_map.iteritems():
            self.buttons[k] = button.Button(self, None, order=(ord, 0), visible=True, text=unicode(k),
                                            border_colour=self.border_colour, border_width=3,
                                            colour=self.colour)
            self.buttons[k + ' key'] = button.Button(self, self.rebind(k), order=(ord, 1), visible=True, text=unicode(pygame.key.name(v)),
                                                     border_colour=self.border_colour, border_width=3,
                                                     colour=self.colour)
            ord += 1

    def rebind(self, action_name):
        def func():
            self.game_class.action_to_rebind = action_name
            self.game_class.GameState = KEYBIND_CAPTURE
            self.buttons[action_name + ' key'].colour = self.active_colour
            self.buttons[action_name + ' key'].border_colour = self.active_border_colour
        return func

    def save(self):
        self.game_class.key_controller.save()

    def load(self):
        self.game_class.key_controller.load()
