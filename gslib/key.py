import pygame

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

        self.keys = collections.defaultdict(bool)  # returns False if key not seen before

        self.key_map = {'Skill Screen': pygame.K_q, 'Show Fear Ranges': pygame.K_r, 'Show Fears': pygame.K_e}
        self.player_map = {'1': {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'possess': pygame.K_f, 'harvest fear': pygame.K_z},
                           '2': {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'possess': pygame.K_g, 'harvest fear': pygame.K_x}}

    def handle_keys(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.keys:
                self.keys[event.key] = True
        if event.type == pygame.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = False

        if self.game.GameState == KEYBIND_CAPTURE:
            self.rebind(event.key)
            self.game.set_state(KEYBIND_MENU)
            return

        if self.keys[pygame.K_ESCAPE] and self.game.GameState != CUTSCENE:
            self.game.set_state(MAIN_MENU)
        if self.keys[pygame.K_m]:
            if self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME:
                self.game.set_state(CUTSCENE)
        if self.keys[self.key_map['Skill Screen']] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.set_state(SKILLS_SCREEN)
        if self.keys[pygame.K_t] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME or self.game.GameState == TEXTBOX_TEST):
            self.game.set_state(TEXTBOX_TEST)
            if self.game.text_box_test.state == TB_ACTIVE:
                self.game.text_box_test.state = TB_CLOSING
            elif self.game.text_box_test.state == TB_INACTIVE:
                self.game.text_box_test.state = TB_STARTING
            print(self.game.text_box_test.state)

        if self.game.GameState == MAIN_GAME:
            self.game.show_fears = self.keys[self.key_map['Show Fears']]
            self.game.show_ranges = self.keys[self.key_map['Show Fear Ranges']]

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
        if new_key == pygame.K_ESCAPE:
            self.game.action_to_rebind = None
            return
        action = self.game.action_to_rebind
        if "Player" in action:  # action = "Player n action"
            n = int(action[7])
            self.player_map[str(n)][action[9:]] = new_key
        else:
            self.key_map[action] = new_key

        self.game.keybind_menu.buttons[action + ' key'].colour = self.game.keybind_menu.colour
        self.game.keybind_menu.buttons[action + ' key'].border_colour = self.game.keybind_menu.border_colour
        self.game.keybind_menu.buttons[action + ' key'].text = pygame.key.name(new_key)

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
                self.game.keybind_menu.buttons[name + ' key'].text = pygame.key.name(val)
            else:
                semi = l.find(';')
                name = l[:semi]
                val = int(l[semi+1:])
                self.game.keybind_menu.buttons[name + ' key'].text = pygame.key.name(val)
                player_n = int(name[7])
                name = name[9:]
                self.player_map[str(player_n)][name] = val
            if not val in self.keys:
                self.keys[val] = False

        f.close()