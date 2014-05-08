import pyglet

from gslib import button
from gslib import slider
from gslib.constants import *
import text


class Menu(object):
    def __init__(self, game, button_size):
        self.game = game
        self.buttons = {}
        self.sliders = {}
        self.button_size = button_size
        self.original_button_size = button_size
        mi = min(button_size[0], button_size[1])
        frac = 8.0/mi
        self.frac = frac
        self.min_button_size = (button_size[0] * frac, button_size[1] * frac)
        self.base_font_size = 14
        self.font_size = self.base_font_size
        self.hori_offset = 60
        self.vert_offset = 40 + button_size[1] + 10
        self.buttons_per_column = ((self.game.dimensions[1] - self.vert_offset) / (self.button_size[1]+20)) - 1

        # TODO: use only one batch with OrderedGroups
        # requires changes to group equality and hash functions to be efficient
        self.sprite_batch = pyglet.graphics.Batch()
        self.text_batch = pyglet.graphics.Batch()

        self._enabled = False

        self.buttons['menu_scale_display'] = button.Button(self, order=(-1, 0), visible=False,
                                                           border_color=(120, 50, 80), border_width=3,
                                                           color=(120, 0, 0), size=(200, 50), pos=(60, 40),
                                                           sprite_batch=self.sprite_batch, text_batch=self.text_batch)
        self.sliders['menu_scale'] = slider.Slider(self, (lambda _: self.arrange_buttons()), range=(1.0, 5.0 / frac),
                                                   order=(-1, 1), value=1.0 / frac, size=(200, 50),
                                                   pos=(60 + 200 + 20, 40), visible=False,
                                                   enabled=self.game.options['menu_scale'],
                                                   sprite_batch=self.sprite_batch)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        if enabled and not self._enabled:
            self.arrange_buttons()
            self.game.window.push_handlers(self)
            self.game.options.push_handlers(self)
        elif not enabled and self._enabled:
            self.game.window.remove_handlers(self)
            self.game.options.remove_handlers(self)
        self._enabled = enabled

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_event((x, y), 'move')

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_event((x, y), 'move')

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_event((x, y), 'down', button)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_event((x, y), 'up', button)

    def draw(self):
        self.sprite_batch.draw()
        self.text_batch.draw()

    def mouse_event(self, pos, typ, button=None):
        for slider in self.sliders.itervalues():
            slider.check_clicked(pos, typ)
        if typ == 'down':
            for button in self.buttons.itervalues():
                if button.check_clicked(pos):
                    return

    def arrange_buttons(self):
        self.buttons['menu_scale_display'].visible = self.game.options['menu_scale']
        self.buttons['menu_scale_display'].enabled = self.game.options['menu_scale']
        self.sliders['menu_scale'].visible = self.game.options['menu_scale']
        self.sliders['menu_scale'].enabled = self.game.options['menu_scale']
        if self.game.options['menu_scale']:
            self.set_menu_scale(self.sliders['menu_scale'].value)
        else:
            self.set_menu_scale(1.0/self.frac)

        self.buttons_per_column = int(((self.game.dimensions[1] - self.vert_offset) / (self.button_size[1]+20))) #- 1

        self.vert_offset = 50 #+ self.game_class.options['menu_scale'] * self.buttons['menu_scale_display'].size[1]

        for button in self.buttons.itervalues():
            if button.order[0] == -1:
                continue
            button.size = self.button_size
            button.font_size = self.font_size
            button.pos = (self.hori_offset + (button.order[1] + int(button.order[0]/self.buttons_per_column)*2)*(self.button_size[0]+20), self.game.dimensions[1] - (self.button_size[1] + self.vert_offset + (button.order[0]%self.buttons_per_column)*(self.button_size[1]+10)))
            if button.text_states:
                button.text = button.text_states[button.text_states_toggle]
        for slider in self.sliders.itervalues():
            if slider.order[0] == -1:
                continue
            slider.size = self.button_size
            slider.pos = (self.hori_offset + (slider.order[1] + int(slider.order[0]/self.buttons_per_column)*2)*(self.button_size[0]+20), self.game.dimensions[1] - (self.button_size[1] + self.vert_offset + (slider.order[0]%self.buttons_per_column)*(self.button_size[1]+10)))

    def set_menu_scale(self, value):
        self.button_size = (self.min_button_size[0] * value, self.min_button_size[1] * value)
        if self.button_size[0] > self.game.dimensions[0] - self.hori_offset - 32:
            self.button_size = (self.game.dimensions[0] - self.hori_offset - 32, self.button_size[1])
        if self.button_size[1] > self.game.dimensions[1] - self.vert_offset - 32:
            self.button_size = (self.button_size[0], self.game.dimensions[1] - self.vert_offset - 32)

        # self.buttons_per_column = int(((self.game_class.dimensions[1] - self.vert_offset) / (self.button_size[1]+20))) #- 1
        self.font_size = int(self.base_font_size * value * self.frac)
        self.buttons['menu_scale_display'].text = u"Menu scale: {}".format(
            round(self.button_size[0] / self.original_button_size[0], 2))

    def on_option_change(self, k, old_value, new_value):
        if k == 'menu_scale':
            self.arrange_buttons()

    def on_resize(self, width, height):
        self.arrange_buttons()


class MainMenu(Menu):
    def __init__(self, game, button_size):
        super(MainMenu, self).__init__(game, button_size)

        common = dict(border_color=(120, 50, 80), border_width=3, color=(120, 0, 0), sprite_batch=self.sprite_batch,
                      text_batch=self.text_batch)

        self.buttons['main_game'] = button.Button(self, self.go_to_main_game, order=(0, 0), text=u'Start Game',
                                                  **common)
        self.buttons['credits'] = button.Button(self, self.go_to_credits, order=(1, 0), text=u'Credits', **common)
        self.buttons['options'] = button.Button(self, self.go_to_options, order=(2, 0), text=u'Options', **common)
        self.buttons['quit'] = button.Button(self, self.game.quit_game, order=(3, 0), text=u'Quit', **common)

        self.arrange_buttons()

        t = 'TODO:\n'
        for l in self.game.TODO:
            t += ' - ' + l + '\n'
        self.todo_sprite = text.new(text=t, font_size=10, width=1000, batch=self.text_batch)
        self.todo_sprite.x, self.todo_sprite.y = (400, 200)

    def go_to_main_game(self):
        self.game.state = MAIN_GAME

    def go_to_credits(self):
        self.game.state = CREDITS

    def go_to_options(self):
        self.game.state = OPTIONS_MENU


class OptionsMenu(Menu):
    def __init__(self, game, button_size):
        super(OptionsMenu, self).__init__(game, button_size)

        common = dict(border_color=(120, 50, 80), border_width=3, color=(120, 0, 0), sprite_batch=self.sprite_batch,
                      text_batch=self.text_batch)

        self.buttons['FOV'] = button.Button(self, self.fov_toggle, order=(0, 0),
                                            text_states=[u'Field of View: No', u'Field of View: Yes'], **common)
        self.buttons['VOF'] = button.Button(self, self.vof_toggle, order=(1, 0),
                                            text_states=[u'View of Field: No', u'View of Field: Yes'], **common)
        self.sliders['VOF_opacity'] = slider.Slider(self, self.vof_value, range=(0, 255), order=(1, 1),
                                                    sprite_batch=self.sprite_batch)
        self.buttons['torch'] = button.Button(self, self.torch_toggle, order=(2, 0),
                                              text_states=[u'Torch: No', u'Torch: Yes'], **common)
        self.buttons['sound_display'] = button.Button(self, order=(3, 0), **common)
        self.buttons['music_display'] = button.Button(self, order=(4, 0), **common)
        self.sliders['sound'] = slider.Slider(self, self.set_sound, range=(0.0, 2.0), order=(3, 1),
                                              sprite_batch=self.sprite_batch)
        self.sliders['music'] = slider.Slider(self, self.set_music, range=(0.0, 2.0), order=(4, 1),
                                              sprite_batch=self.sprite_batch)
        self.buttons['menu_scale'] = button.Button(self, self.menu_scale_toggle, order=(5, 0),
                                                   text_states=[u'Menu Scaling: Off', u'Menu Scaling: On'], **common)
        self.buttons['key_bind'] = button.Button(self, self.keybind_toggle, order=(6, 0), text=u'Keybind Menu',
                                                 **common)
        self.buttons['load'] = button.Button(self, self.load, order=(7, 0), text=u'Load Options', **common)
        self.buttons['save'] = button.Button(self, self.save, order=(7, 1), text=u'Save Options', **common)
        self.buttons['screen_size_display'] = button.Button(self, order=(8, 0), text=u'Screen Size', **common)
        self.buttons['screen_size'] = button.Button(self, self.set_screen_size, order=(8, 1),
                                                    text_states=[u'1024 x 768', u'1280 x 720', u'1600 x 900',
                                                                 u'1920 x 1080'], **common)
        self.buttons['vsync'] = button.Button(self, self.vsync_toggle, order=(9, 0),
                                              text_states=[u'vsync: Off', u'vsync: On'], **common)
        self.buttons['fullscreen'] = button.Button(self, self.fullscreen_toggle, order=(10, 0),
                                                   text_states=[u'fullscreen: Off', u'fullscreen: On'], **common)
        self.buttons['reset'] = button.Button(self, self.reset, order=(11, 0), text=u'Reset Options', **common)

        self.arrange_buttons()

    def fov_toggle(self):
        self.game.options['FOV'] = not self.game.options['FOV']

    def vof_toggle(self):
        self.game.options['VOF'] = not self.game.options['VOF']

    def vof_value(self, val):
        self.game.options['VOF_opacity'] = val

    def torch_toggle(self):
        self.game.options['torch'] = not self.game.options['torch']

    def keybind_toggle(self):
        self.game.state = KEYBIND_MENU

    def menu_scale_toggle(self):
        self.game.options['menu_scale'] = not self.game.options['menu_scale']

    def set_sound(self, value):
        self.game.options['sound_volume'] = value

    def set_music(self, value):
        self.game.options['music_volume'] = value

    def vsync_toggle(self):
        self.game.options['vsync'] = not self.game.options['vsync']

    def fullscreen_toggle(self):
        self.game.options['fullscreen'] = not self.game.options['fullscreen']

    def update_button_text_and_slider_values(self):
        self.buttons['FOV'].text_states_toggle = self.game.options['FOV']
        self.buttons['VOF'].text_states_toggle = self.game.options['VOF']
        self.sliders['VOF_opacity'].visible = self.game.options['VOF']
        self.sliders['VOF_opacity'].value = self.game.options['VOF_opacity']
        self.buttons['torch'].text_states_toggle = self.game.options['torch']
        self.buttons['menu_scale'].text_states_toggle = self.game.options['menu_scale']
        self.buttons['vsync'].text_states_toggle = self.game.options['vsync']
        self.buttons['fullscreen'].text_states_toggle = self.game.options['fullscreen']

        self.buttons['sound_display'].text = \
            u'Sound Volume: {}'.format(int(self.game.options['sound_volume'] / 0.003))
        self.buttons['music_display'].text = \
            u'Music Volume: {}'.format(int(self.game.options['music_volume'] / 0.003))

        self.sliders['sound'].value = self.game.options['sound_volume']
        self.sliders['music'].value = self.game.options['music_volume']

        size = "{} x {}".format(*self.game.options['resolution'])
        if size in self.buttons['screen_size'].text_states:
            new_index = self.buttons['screen_size'].text_states.index(size) + 1
            self.buttons['screen_size'].text_states_toggle = new_index % len(self.buttons['screen_size'].text_states)
        else:
            self.buttons['screen_size'].text_states_toggle = 0

    def load(self):
        self.game.options.load_options()

    def save(self):
        self.game.options.save_options()

    def reset(self):
        # not using .update() to ensure .__setitem__() is called
        for k, v in DEFAULT_OPTIONS.iteritems():
            self.game.options[k] = v

    def set_screen_size(self):
        new_size = self.buttons['screen_size'].text_states[self.buttons['screen_size'].text_states_toggle]
        if 'x' in new_size:
            new_size = new_size.split(' x ')
            new_size = (int(new_size[0]), int(new_size[1]))
            self.game.options['resolution'] = new_size

    def arrange_buttons(self):
        self.update_button_text_and_slider_values()
        super(OptionsMenu, self).arrange_buttons()

    def on_option_change(self, k, old_value, new_value):
        if not self.enabled:
            return
        self.update_button_text_and_slider_values()
        super(OptionsMenu, self).on_option_change(k, old_value, new_value)


class SkillsMenu(Menu):
    def __init__(self, game, button_size):
        super(SkillsMenu, self).__init__(game, button_size)
        temp_order = 0
        for skill in self.game.skills_dict:
            if skill in self.game.players['player1'].skills_learnt:
                skill_color = LEARNT_SKILL_COLOR
            elif self.game.skills_dict[skill].can_be_learnt(self.game.players['player1']):
                skill_color = CAN_BE_LEARNT_COLOR
            else:
                skill_color = UNLEARNABLE_COLOR
            f = lambda skill2=skill: self.learn_skill(skill2)
            self.buttons[skill] = button.Button(self, f,
                                                text=skill + " cost:" + str(self.game.skills_dict[skill].cost),
                                                border_color=(120, 50, 80), border_width=3, color=skill_color,
                                                order=(temp_order, 0), sprite_batch=self.sprite_batch,
                                                text_batch=self.text_batch)
            self.buttons[skill + "_description"] = button.Button(self, None,
                                                                 text=self.game.skills_dict[skill].description,
                                                                 border_color=(120, 50, 80), border_width=3,
                                                                 color=(30, 120, 140), order=(temp_order, 1),
                                                                 sprite_batch=self.sprite_batch,
                                                                 text_batch=self.text_batch)
            temp_order += 1
        self.arrange_buttons()

    def learn_skill(self, skill):
        self.game.players['player1'].learn_skill(skill)
        print(self.game.players['player1'].skills_learnt)

        for skill in self.buttons:
            if self.buttons[skill].order[0] != -1 and self.buttons[skill].order[1] == 0:
                if skill in self.game.players['player1'].skills_learnt:
                    skill_color = LEARNT_SKILL_color
                elif self.game.skills_dict[skill].can_be_learnt(self.game.players['player1']):
                    skill_color = CAN_BE_LEARNT_color
                else:
                    skill_color = UNLEARNABLE_color
                self.buttons[skill].color = skill_color


class KeyBindMenu(Menu):
    def __init__(self, game, button_size):
        super(KeyBindMenu, self).__init__(game, button_size)
        self.border_color = (120, 50, 80)
        self.color = (120, 0, 0)

        self.active_border_color = (50, 120, 80)
        self.active_color = (0, 120, 0)

        self.create_buttons()

        self.arrange_buttons()

    def create_buttons(self):
        common = dict(border_color=self.border_color, border_width=3, color=self.color,
                      sprite_batch=self.sprite_batch, text_batch=self.text_batch)
        ord = 0
        self.buttons['load'] = button.Button(self, self.load, order=(ord, 0), text=u'Load', **common)
        self.buttons['save'] = button.Button(self, self.save, order=(ord, 1), text=u'Save', **common)
        ord += 1
        for player, p_map in self.game.key_controller.player_map.iteritems():
            for k, v in p_map.iteritems():
                name = 'Player ' + str(player) + ' ' + k
                self.buttons[name] = button.Button(self, order=(ord, 0), text=unicode(name), **common)
                self.buttons[name + ' key'] = button.Button(self, self.rebind(name), order=(ord, 1),
                                                            text=unicode(pyglet.window.key.symbol_string(p_map[k])),
                                                            **common)
                ord += 1

        for k, v in self.game.key_controller.key_map.iteritems():
            self.buttons[k] = button.Button(self, order=(ord, 0), text=unicode(k), **common)
            self.buttons[k + ' key'] = button.Button(self, self.rebind(k), order=(ord, 1),
                                                     text=unicode(pyglet.window.key.symbol_string(v)), **common)
            ord += 1

    def rebind(self, action_name):
        def func():
            self.game.action_to_rebind = action_name
            self.game.state = KEYBIND_CAPTURE
            self.buttons[action_name + ' key'].color = self.active_color
            self.buttons[action_name + ' key'].border_color = self.active_border_color
        return func

    def save(self):
        self.game.key_controller.save()

    def load(self):
        self.game.key_controller.load()
