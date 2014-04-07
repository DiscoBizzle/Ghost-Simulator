import pygame

from gslib.constants import *


class KeyController(object):
    def __init__(self, game):
        self.game = game

        self.keys = {pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False,
                     pygame.K_ESCAPE: False, pygame.K_m: False, pygame.K_q: False, pygame.K_t: False,
                     pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False, pygame.K_e: False,
                     pygame.K_r: False}

        self.key_map = {'Skill Screen': pygame.K_q, 'Show Fear Ranges': pygame.K_r, 'Show Fears': pygame.K_e}
        self.player_map = {0: {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT},
                           1: {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d}}

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
        if self.keys[pygame.K_t] and (self.game.GameState == MAIN_MENU or self.game.GameState == MAIN_GAME):
            self.game.set_state(TEXTBOX_TEST)

        if self.game.GameState == MAIN_GAME:
            self.game.show_fears = self.keys[self.key_map['Show Fears']]
            self.game.show_ranges = self.keys[self.key_map['Show Fear Ranges']]

        for i, p in enumerate(self.game.players):
            p.move_down = self.keys[self.player_map[i]['down']]
            p.move_up = self.keys[self.player_map[i]['up']]
            p.move_left = self.keys[self.player_map[i]['left']]
            p.move_right = self.keys[self.player_map[i]['right']]

    def rebind(self, new_key):
        if new_key == pygame.K_ESCAPE:
            self.game.action_to_rebind = None
            return
        action = self.game.action_to_rebind
        if "Player" in action:  # action = "Player n action"
            n = int(action[7])
            self.player_map[n][action[9:]] = new_key
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
                self.player_map[player_n][name] = val

        f.close()