# import pygame
import pyglet
import pyglet.window.key as Pkey

from gslib.constants import *
import collections


class KeyController(object):
    def __init__(self, game):
        """ To add new key, add to either:
         - key_map: for player-independent keys
         - player_map: for player-dependent keys

        Name used in dict will show up in keybind menu.

        Add function to do what you want.
        Add logic to handle_keys to direct to said function.
        """

        self.game = game

        self.keys = Pkey.KeyStateHandler()
        self.key_map = {'Skill Screen': Pkey.Q, 'Show Fear Ranges': Pkey.R, 'Show Fears': Pkey.E,
                        'Toggle Editor': Pkey.B, 'Snap to Grid': Pkey.LCTRL}
        self.player_map = {'1': {'up': Pkey.UP, 'down': Pkey.DOWN, 'left': Pkey.LEFT, 'right': Pkey.RIGHT, 'possess': Pkey.F, 'harvest fear': Pkey.Z},
                           '2': {'up': Pkey.W, 'down': Pkey.S, 'left': Pkey.A, 'right': Pkey.D, 'possess': Pkey.Q, 'harvest fear': Pkey.X}}

        self.game.window.push_handlers(self)

    def on_key_press(self, symbol, modifiers):
        self.keys.on_key_press(symbol, modifiers)
        self.handle_keys(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.keys.on_key_release(symbol, modifiers)
        self.handle_keys(symbol, modifiers)

    def handle_keys(self, symbol, modifiers):

        if self.game.state == KEYBIND_CAPTURE:
            self.rebind(symbol)
            self.game.state = KEYBIND_MENU
            return

        if self.keys[Pkey.ESCAPE] and self.game.state != CUTSCENE:
            self.game.state = MAIN_MENU
        if self.keys[Pkey.M]:
            if self.game.state == MAIN_MENU or self.game.state == MAIN_GAME:
                self.game.state = CUTSCENE
        if self.keys[self.key_map['Skill Screen']] and (self.game.state == MAIN_MENU or self.game.state == MAIN_GAME):
            self.game.state = SKILLS_SCREEN
        if self.keys[Pkey.T] and (self.game.state == MAIN_MENU or self.game.state == MAIN_GAME or self.game.state == TEXTBOX_TEST):
            self.game.state = TEXTBOX_TEST
            if self.game.text_box_test.state == TB_ACTIVE:
                self.game.text_box_test.state = TB_CLOSING
            elif self.game.text_box_test.state == TB_INACTIVE:
                self.game.text_box_test.state = TB_STARTING
            print(self.game.text_box_test.state)

        if self.game.state == MAIN_GAME:
            self.game.show_fears = self.keys[self.key_map['Show Fears']]
            self.game.show_ranges = self.keys[self.key_map['Show Fear Ranges']]
            if self.keys[self.key_map['Toggle Editor']]:
                self.game.editor_active = not self.game.editor_active
                self.game.gather_buttons_and_drop_lists_and_objects()

        for k, p in self.game.players.iteritems():
            p.move_down = self.keys[self.player_map[k[-1]]['down']]
            p.move_up = self.keys[self.player_map[k[-1]]['up']]
            p.move_left = self.keys[self.player_map[k[-1]]['left']]
            p.move_right = self.keys[self.player_map[k[-1]]['right']]

            if self.keys[self.player_map[k[-1]]['harvest fear']]:
                p.harvest_fear()

            if self.keys[self.player_map[k[-1]]['possess']]:
                if p.possess_key_up:
                    p.toggle_possess()
                    p.possess_key_up = False  # not self.keys[self.player_map[i]['possess']]
            else:
                p.possess_key_up = True

    def rebind(self, new_key):
        if new_key == Pkey.ESCAPE:
            self.game.action_to_rebind = None
            return
        action = self.game.action_to_rebind
        if "Player" in action:  # action = "Player n action"
            n = action[7]
            self.player_map[n][action[9:]] = new_key
        else:
            self.key_map[action] = new_key

        self.game.keybind_menu.buttons[action + ' key'].colour = self.game.keybind_menu.colour
        self.game.keybind_menu.buttons[action + ' key'].border_colour = self.game.keybind_menu.border_colour
        self.game.keybind_menu.buttons[action + ' key'].text = Pkey.symbol_string(new_key)

        self.keys[new_key] = False
        self.game.action_to_rebind = None

    def save(self):
        f = open(KEYMAP_FILE, 'w')
        for player, p_map in self.player_map.iteritems():
            for k, v in p_map.iteritems():
                name = 'Player ' + str(player) + ' ' + k
                f.write(name + ';' + str(v) + '\n')

        f.write('#\n')
        for k, v in self.key_map.iteritems():
            f.write(k + ';' + str(v) + '\n')

        f.close()

    def load(self):
        f = open(KEYMAP_FILE, 'r')
        game_options = False
        for l in f:
            if '#' in l:
                game_options = True
                continue
            if game_options:
                semi = l.find(';')
                name = l[:semi]
                val = int(l[semi+1:])
                self.key_map[name] = val
                self.game.keybind_menu.buttons[name + ' key'].text = Pkey.symbol_string(val)
            else:
                semi = l.find(';')
                name = l[:semi]
                val = int(l[semi+1:])
                self.game.keybind_menu.buttons[name + ' key'].text = Pkey.symbol_string(val)
                player_n = int(name[7])
                name = name[9:]
                self.player_map[str(player_n)][name] = val
            if not val in self.keys:
                self.keys[val] = False

        f.close()