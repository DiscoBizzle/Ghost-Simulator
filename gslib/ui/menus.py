from __future__ import absolute_import, division, print_function

import pyglet

from gslib.constants import *
from gslib.engine import text
from gslib.ui import button, slider, drop_down_list
from gslib import options, window


class MenuButton(button.Button):
    def __init__(self, order=(0, 0), border_color=(120, 50, 80), border_width=3, color=(120, 0, 0), text_font=FONT,
                 text_color=(200, 200, 200, 255), **kwargs):
        self.order = order
        super(MenuButton, self).__init__(border_color=border_color, border_width=border_width, color=color,
                                         window=window, text_font=text_font, text_color=text_color, **kwargs)


class MenuSlider(slider.Slider):
    def __init__(self, order=(0, 0), **kwargs):
        self.order = order
        super(MenuSlider, self).__init__(window=window, **kwargs)


class MenuLabel(MenuButton):

    # FIXME: currently nuking button handlers until a Labal control is made
    def create_handlers(self):
        pass

    def delete_handlers(self):
        pass


class MenuDropDownList(drop_down_list.DropDownList):
    def __init__(self, order=(0, 0), **kwargs):
        super(MenuDropDownList, self).__init__(window=window, **kwargs)
        self.order = order


class Menu(object):
    def __init__(self, game, button_size):
        self.game = game
        self.controls = {}
        self.button_size = button_size
        self.original_button_size = button_size
        mi = min(button_size[0], button_size[1])
        frac = 8 / mi
        self.frac = frac
        self.min_button_size = (button_size[0] * frac, button_size[1] * frac)
        self.base_font_size = 14
        self.font_size = self.base_font_size
        self.hori_offset = 60
        self.vert_offset = 40 + button_size[1] + 10
        self.buttons_per_column = ((window.height - self.vert_offset) // (self.button_size[1] + 20)) - 1

        self.batch = pyglet.graphics.Batch()

        self._enabled = False

        self.controls['menu_scale_display'] = MenuLabel(order=(-1, 0), pos=(60, 40), size=(200, 50), batch=self.batch)
        self.controls['menu_scale'] = MenuSlider(order=(-1, 1), function=(lambda _: self.arrange_buttons()),
                                                 pos=(60 + 200 + 20, 40), range=(1, 5 / frac), value=1 / frac,
                                                 size=(200, 50), batch=self.batch)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        if enabled == self._enabled:
            return
        self._enabled = enabled
        if enabled:
            window.push_handlers(self)
            options.push_handlers(self)
            for control in self.controls.itervalues():
                control.enabled = True
            self.arrange_buttons()
        else:
            for control in self.controls.itervalues():
                control.enabled = False
            window.remove_handlers(self)
            options.remove_handlers(self)

    def on_draw(self):
        window.clear()
        self.batch.draw()

    def arrange_buttons(self):
        self.controls['menu_scale_display'].visible = options['menu_scale']
        self.controls['menu_scale_display'].enabled = options['menu_scale']
        self.controls['menu_scale'].visible = options['menu_scale']
        self.controls['menu_scale'].enabled = options['menu_scale']
        if options['menu_scale']:
            self.set_menu_scale(self.controls['menu_scale'].value)
        else:
            self.set_menu_scale(1 / self.frac)

        self.buttons_per_column = (window.height - self.vert_offset) // (self.button_size[1] + 20) #- 1

        self.vert_offset = 50 #+ self.game_class.options['menu_scale'] * self.buttons['menu_scale_display'].size[1]

        for control in self.controls.itervalues():
            if control.order[0] == -1:
                continue
            control.size = self.button_size
            control.pos = (self.hori_offset + (control.order[1] + (control.order[0] // self.buttons_per_column) * 2) * (self.button_size[0] + 20),
                           window.height - (self.button_size[1] + self.vert_offset + (control.order[0] % self.buttons_per_column) * (self.button_size[1] + 10)))
            if isinstance(control, button.Button):
                control.font_size = self.font_size

    def set_menu_scale(self, value):
        self.button_size = (self.min_button_size[0] * value, self.min_button_size[1] * value)
        if self.button_size[0] > window.width - self.hori_offset - 32:
            self.button_size = (window.width - self.hori_offset - 32, self.button_size[1])
        if self.button_size[1] > window.height - self.vert_offset - 32:
            self.button_size = (self.button_size[0], window.height - self.vert_offset - 32)

        # self.buttons_per_column = int(((self.game_class.dimensions[1] - self.vert_offset) / (self.button_size[1]+20))) #- 1
        self.font_size = int(self.base_font_size * value * self.frac)
        self.controls['menu_scale_display'].text = u"Menu scale: {}".format(
            round(self.button_size[0] / self.original_button_size[0], 2))

    def on_option_change(self, key, value):
        if key == 'menu_scale':
            self.arrange_buttons()

    def on_resize(self, width, height):
        self.arrange_buttons()


class MainMenu(Menu):
    def __init__(self, game, button_size):
        super(MainMenu, self).__init__(game, button_size)

        self.controls['main_game'] = MenuButton(order=(0, 0), function=self.go_to_main_game, text=u'Start Game',
                                                batch=self.batch)
        self.controls['credits'] = MenuButton(order=(1, 0), function=self.go_to_credits, text=u'Credits',
                                              batch=self.batch)
        self.controls['options'] = MenuButton(order=(2, 0), function=self.go_to_options, text=u'Options',
                                              batch=self.batch)
        self.controls['quit'] = MenuButton(order=(3, 0), function=self.game.quit_game, text=u'Quit',
                                           batch=self.batch)

        self.arrange_buttons()

        t = 'TODO:\n'
        for l in self.game.TODO:
            t += ' - ' + l + '\n'
        self.todo_sprite = text.new(text=t, font_size=10, width=1000, batch=self.batch)
        self.todo_sprite.x, self.todo_sprite.y = (400, 200)

    def go_to_main_game(self):
        self.game.state = MAIN_GAME

    def go_to_credits(self):
        self.game.state = CREDITS

    def go_to_options(self):
        self.game.state = OPTIONS_MENU


class OptionsMenuToggleCheckBox(MenuButton):
    def __init__(self, option_key=None, display_text=None, **kwargs):
        self.option_key = option_key
        self.display_text = display_text
        super(OptionsMenuToggleCheckBox, self).__init__(function=self.toggle_option, text=self.create_text(), **kwargs)

    def on_option_change(self, key, value):
        if key == self.option_key:
            self.text = self.create_text()

    def create_text(self):
        if options[self.option_key]:
            return u"{}: Yes".format(self.display_text)
        else:
            return u"{}: No".format(self.display_text)

    def toggle_option(self):
        options[self.option_key] = not options[self.option_key]

    def update(self):
        self.text = self.create_text()
        super(OptionsMenuToggleCheckBox, self).update()

    def create_handlers(self):
        options.push_handlers(self)
        super(OptionsMenuToggleCheckBox, self).create_handlers()

    def delete_handlers(self):
        options.remove_handlers(self)
        super(OptionsMenuToggleCheckBox, self).delete_handlers()


class OptionsMenu(Menu):
    def __init__(self, game, button_size):
        super(OptionsMenu, self).__init__(game, button_size)

        self._create_controls()

        self.arrange_buttons()

    def _create_controls(self):
        self.controls['FOV'] = OptionsMenuToggleCheckBox(order=(0, 0), option_key='FOV', display_text=u'Field of View',
                                                         batch=self.batch)
        self.controls['VOF'] = OptionsMenuToggleCheckBox(order=(1, 0), option_key='VOF', display_text=u'View of Field',
                                                         batch=self.batch)
        self.controls['VOF_opacity'] = MenuSlider(order=(1, 1), function=self.vof_value, range=(0, 255),
                                                  batch=self.batch)
        self.controls['vsync'] = OptionsMenuToggleCheckBox(order=(2, 0), option_key='vsync', display_text=u'VSync',
                                                           batch=self.batch)
        self.controls['fullscreen'] = OptionsMenuToggleCheckBox(order=(3, 0), option_key='fullscreen',
                                                                display_text='Fullscreen', batch=self.batch)
        self.controls['screen_size_display'] = MenuLabel(order=(4, 0), text=u'Screen Size:', batch=self.batch)
        pos_res = [(1024, 768), (1280, 720), (1600, 900), (1920, 1080)]
        self.controls['screen_size'] = MenuDropDownList(order=(4, 1), items=pos_res, function=self.set_screen_size,
                                                        batch=self.batch)

        self.controls['sound_display'] = MenuLabel(order=(5, 0), batch=self.batch)
        self.controls['sound'] = MenuSlider(order=(5, 1), function=self.set_sound, range=(0.0, 2.0), batch=self.batch)
        self.controls['music_display'] = MenuLabel(order=(6, 0), batch=self.batch)
        self.controls['music'] = MenuSlider(order=(6, 1), function=self.set_music, range=(0.0, 2.0), batch=self.batch)

        self.controls['torch'] = OptionsMenuToggleCheckBox(order=(7, 0), option_key='torch', display_text=u'Torch',
                                                           batch=self.batch)
        self.controls['menu_scale_option'] = OptionsMenuToggleCheckBox(order=(8, 0), option_key='menu_scale',
                                                                       display_text=u'Menu Scaling', batch=self.batch)

        self.controls['key_bind'] = MenuButton(order=(9, 0), function=self.keybind_toggle, text=u'Keybind Menu',
                                               batch=self.batch)

        self.controls['load'] = MenuButton(order=(10, 0), function=options.load_options, text=u'Load Options',
                                           batch=self.batch)
        self.controls['save'] = MenuButton(order=(10, 1), function=options.save_options, text=u'Save Options',
                                           batch=self.batch)
        self.controls['reset'] = MenuButton(order=(11, 0), function=options.reset_options, text=u'Reset Options',
                                            batch=self.batch)

    @staticmethod
    def vof_value(val):
        options['VOF_opacity'] = val

    def keybind_toggle(self):
        self.game.state = KEYBIND_MENU

    @staticmethod
    def set_sound(value):
        options['sound_volume'] = value

    @staticmethod
    def set_music(value):
        options['music_volume'] = value

    def update_controls(self):
        self.controls['VOF_opacity'].visible = options['VOF']
        self.controls['VOF_opacity'].value = options['VOF_opacity']

        self.controls['sound_display'].text = \
            u'Sound Volume: {}'.format(int(options['sound_volume'] / 0.003))
        self.controls['music_display'].text = \
            u'Music Volume: {}'.format(int(options['music_volume'] / 0.003))

        self.controls['sound'].value = options['sound_volume']
        self.controls['music'].value = options['music_volume']

        self.controls['screen_size'].selected_name = u"{}\u00D7{}".format(*options['resolution'])

    def set_screen_size(self):
        if self.controls['screen_size'].selected is not None:
            options['resolution'] = self.controls['screen_size'].selected

    def arrange_buttons(self):
        self.update_controls()
        super(OptionsMenu, self).arrange_buttons()

    def on_option_change(self, key, value):
        self.update_controls()
        super(OptionsMenu, self).on_option_change(key, value)


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
            self.controls[skill] = MenuButton(function=f,
                                                text=skill + " cost:" + str(self.game.skills_dict[skill].cost),
                                                border_color=(120, 50, 80), border_width=3, color=skill_color,
                                                order=(temp_order, 0), batch=self.batch)
            self.controls[skill + "_description"] = MenuButton(function=None,
                                                                 text=self.game.skills_dict[skill].description,
                                                                 border_color=(120, 50, 80), border_width=3,
                                                                 color=(30, 120, 140), order=(temp_order, 1),
                                                                 batch=self.batch)
            temp_order += 1
        self.arrange_buttons()

    def learn_skill(self, skill):
        self.game.players['player1'].learn_skill(skill)
        print(self.game.players['player1'].skills_learnt)

        for skill in self.controls:
            if self.controls[skill].order[0] != -1 and self.controls[skill].order[1] == 0:
                if skill in self.game.players['player1'].skills_learnt:
                    skill_color = LEARNT_SKILL_COLOR
                elif self.game.skills_dict[skill].can_be_learnt(self.game.players['player1']):
                    skill_color = CAN_BE_LEARNT_COLOR
                else:
                    skill_color = UNLEARNABLE_COLOR
                self.controls[skill].color = skill_color


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
        order = 0
        self.controls['load'] = MenuButton(function=self.load, order=(order, 0), text=u'Load', batch=self.batch)
        self.controls['save'] = MenuButton(function=self.save, order=(order, 1), text=u'Save', batch=self.batch)
        order += 1
        for player, p_map in self.game.key_controller.player_map.iteritems():
            for k, v in p_map.iteritems():
                name = 'Player ' + str(player) + ' ' + k
                self.controls[name] = MenuButton(order=(order, 0), text=unicode(name), batch=self.batch)
                self.controls[name + ' key'] = MenuButton(function=self.rebind(name), order=(order, 1),
                                                            text=unicode(pyglet.window.key.symbol_string(p_map[k])),
                                                            batch=self.batch)
                order += 1

        for k, v in self.game.key_controller.key_map.iteritems():
            self.controls[k] = MenuButton(order=(order, 0), text=unicode(k), batch=self.batch)
            self.controls[k + ' key'] = MenuButton(function=self.rebind(k), order=(order, 1),
                                                     text=unicode(pyglet.window.key.symbol_string(v)), batch=self.batch)
            order += 1

    def rebind(self, action_name):
        def func():
            self.game.action_to_rebind = action_name
            self.game.state = KEYBIND_CAPTURE
            self.controls[action_name + ' key'].color = self.active_color
            self.controls[action_name + ' key'].border_color = self.active_border_color
        return func

    def save(self):
        self.game.key_controller.save()

    def load(self):
        self.game.key_controller.load()
