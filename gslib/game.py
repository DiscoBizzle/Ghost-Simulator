import os
import os.path
import sys
import time

import pygame

from gslib import button
from gslib import character
from gslib import credits
from gslib import graphics
from gslib import joy
from gslib import maps
from gslib import menus
from gslib import player
from gslib import skills
from gslib import sound
from gslib import text_box
from gslib import key
from gslib import mouse
from gslib import fear_functions
from gslib import text_functions
from gslib.constants import *


# doesn't seem to be needed any more
#if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:
#    # On NT like Windows versions smpeg video needs windb. --
#os.environ['SDL_VIDEODRIVER'] = ''
#os.environ['SDL_VIDEODRIVER'] = ''


class Game(object):
    """
    To draw something relative to map: (accounts for camera)
    game.world_objects_to_draw.append((surface, position))

    To draw something relative to game screen:
    game.screen_objects_to_draw.append((surface, position))

    Objects will be drawn without having to add them to these lists.
    """
    def __init__(self):

        self.options = {'FOV': True, 'VOF': False, 'torch': False, 'menu_scale': False}
        self.dimensions = (GAME_WIDTH, GAME_HEIGHT)

        self.Menu = menus.MainMenu(self, (161, 100))
        self.GameState = MAIN_MENU
        self.cutscene_started = False
        self.cutscene_next = os.path.join(VIDEO_DIR, "default.mpg")
        self.game_running = True
        self.graphics = graphics.Graphics(self)
        pygame.display.set_caption("Ghost Simulator v. 0.000000001a")
        self.music_list = sound.get_music_list()
        self.sound_dict = sound.load_all_sounds()
        self.credits = credits.Credits(self)
        self.options_menu = menus.OptionsMenu(self, (200, 50))


        self.clock = pygame.time.Clock()
        self.ms_passed = 0

        self.fps_clock = pygame.time.Clock()

        self.camera_coords = (0, 0)

        self.players = {}
        self.players['player1'] = player.Player(self, TILE_SIZE*6, TILE_SIZE*18, 16, 16, 'GhostSheet.png')
        self.players['player2'] = player.Player(self, 0, 0, 16, 16, 'TutorialGhost2.png')
        # self.player1 = self.players[0]

        self.objects = dict(self.players.items())

        self.skills_dict = skills.load_skill_dict()
        self.SkillMenu = menus.SkillsMenu(self, (200,150))

        # for i in range(5):
        #     self.objects.append(character.Character(self, 0, 0, 16, 16, character.gen_character()))

        self.text_box_test = text_box.TextBox("Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go.")

        self.text_box_test.create_background_surface()

        self.disp_object_stats = False
        self.object_stats = None


        self.key_controller = key.KeyController(self)
        # HACK
        self.keys = self.key_controller.keys

        self.keybind_menu = menus.KeyBindMenu(self, (190, 40))
        self.action_to_rebind = None

        self.mouse_controller = mouse.MouseController(self)

        self.joy_controller = joy.JoyController(self)

        self.event_map = {
            pygame.KEYDOWN: self.key_controller.handle_keys,
            pygame.KEYUP: self.key_controller.handle_keys,
            pygame.QUIT: (lambda _: self.quit_game()),
            pygame.MOUSEBUTTONDOWN: self.mouse_controller.mouse_click,
            pygame.MOUSEBUTTONUP: self.mouse_controller.mouse_up,
            pygame.MOUSEMOTION: self.mouse_controller.mouse_move,
            pygame.JOYHATMOTION: self.joy_controller.handle_hat,
            pygame.JOYBUTTONDOWN: self.joy_controller.handle_buttondown,
            pygame.JOYBUTTONUP: self.joy_controller.handle_buttonup,
            pygame.JOYAXISMOTION: self.joy_controller.handle_axis,
            pygame.JOYBALLMOTION: self.joy_controller.handle_ball,
            pygame.VIDEORESIZE: self.graphics.resize_window,
        }

        sound.start_next_music(self.music_list)

        self.map_list = []
        self.map_list.append(maps.Map(os.path.join(TILES_DIR, 'level2.png'), os.path.join(TILES_DIR, 'level3.json'), self))
        self.map_list.append(maps.Map(os.path.join(TILES_DIR, 'level2.png'), os.path.join(TILES_DIR, 'level2.json'), self))
        self.map_list.append(maps.Map(os.path.join(TILES_DIR, 'martin.png'), os.path.join(TILES_DIR, 'martin.json'), self))

        self.map_index = 0
        self.map = self.map_list[self.map_index]

        self.buttons = {
            'change_map': button.Button(self, self.change_map, pos=(0, 0), size=(20, 20), visible=True,
                                        text=u'M', border_colour=(120, 50, 80), border_width=3,
                                        colour=(120, 0, 0), enabled=True)}

        # self.toPossess = None
        self.selected_object = None

        self.world_objects_to_draw = []
        self.screen_objects_to_draw = []
        self.objects = dict(self.objects.items() + self.map.objects.items())

        self.show_fears = False
        self.show_ranges = False

        self.load_options()
        self.key_controller.load()

        self.touching = []
        self.last_touching = []

    def game_loop(self):
        while self.game_running:
            # Update clock & pump event queue.
            # We cannot do this at the same time as playing a cutscene on linux; pygame.movie is shite.
            if not (self.GameState == CUTSCENE and (
                        sys.platform == "linux2" or sys.platform == "linux" or sys.platform == "linux3")):
                self.clock.tick()
                self.ms_passed += self.clock.get_time()

                for event in pygame.event.get():
                    response = self.event_map.get(event.type)
                    if response is not None:
                        response(event)

            if self.GameState == CUTSCENE:
                self.graphics.draw_cutscene()
                time.sleep(0.001)
            elif self.ms_passed > 33:
                self.update()
                self.ms_passed = 0

                self.fps_clock.tick()
                self.graphics.main_game_draw()
            else:
                time.sleep(0.001)  # note: sleeping not only a good idea but necessary for pygame.movie os x

    def update(self):
        # this is fixed timestep, 30 FPS. if game runs slower, we lag.
        # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
        #self.objects.append(character.Character(self, 50, 50, 16, 16, character.gen_character()))
        self.camera_coords = self.calc_camera_coord()
        if self.show_fears:
            self.say_fears()
        if self.show_ranges:
            self.show_fear_ranges()

        if self.GameState == MAIN_GAME:
            self.last_touching = [p for p in self.touching]  # creates a copy
            for obj in self.objects.itervalues():
                obj.update()

            for i, p in enumerate(self.touching):
                if not p in self.last_touching:  # detect on touch
                    if p[0].has_touched_function:
                        for f in p[0].has_touched_function:
                            f(p[1])
                            #p[0].has_touched_function(p[1])
                    if p[1].is_touched_function:
                        for f in p[1].is_touched_function:
                            f(p[0]) # p[1].is_touched_function(p[0])

            for i, p in enumerate(self.last_touching):
                if not p in self.touching:  # detect on un-touch
                    if p[0].has_untouched_function:
                        for f in p[0].has_untouched_function:
                            f(p[1])
                            # p[0].has_untouched_function(p[1])
                    if p[1].is_untouched_function:
                        for f in p[1].is_untouched_function:
                            f(p[0])
                            # p[1].is_untouched_function(p[0])

        elif self.GameState == CREDITS:
            self.credits.update()
        elif self.GameState == TEXTBOX_TEST:
            self.text_box_test.update()

    def calc_camera_coord(self):
        avg_pos = [0, 0]
        c = 0
        for p in self.players.itervalues():
            c += 1
            avg_pos[0] += p.coord[0]
            avg_pos[1] += p.coord[1]

        avg_pos = (avg_pos[0] / c, avg_pos[1] / c)
        # coord = (self.player1.coord[0] - (self.dimensions[0]/2), self.player1.coord[1] - (self.dimensions[1]/2))
        coord = (avg_pos[0] - (self.dimensions[0]/2), avg_pos[1] - (self.dimensions[1]/2))
        pad = (32, 32, 32, 96)  # left right up down

        # bottom
        if avg_pos[1] > LEVEL_HEIGHT - self.dimensions[1]/2 + pad[3]:
            coord = (coord[0], LEVEL_HEIGHT - self.dimensions[1] + pad[3])

        # right
        if avg_pos[0] > LEVEL_WIDTH - self.dimensions[0]/2 + pad[1]:
            coord = (LEVEL_WIDTH - self.dimensions[0] + pad[1], coord[1])

        # left
        if avg_pos[0] < self.dimensions[0]/2 - pad[0] or LEVEL_WIDTH < self.dimensions[0] - pad[0] - pad[1]:
            coord = (-pad[0], coord[1])

        # top
        if avg_pos[1] < self.dimensions[1]/2 - pad[2] or LEVEL_HEIGHT < self.dimensions[1] - pad[2] - pad[3]:
            coord = (coord[0], -pad[2])

        return coord

    def say_fears(self):
        for o in self.objects.itervalues():
            if isinstance(o, player.Player):
                surf = text_functions.speech_bubble("Oonce oonce oonce oonce!", 200)
                pos = (o.coord[0] + o.dimensions[0], o.coord[1] - surf.get_height())
                self.world_objects_to_draw.append((surf, pos))
                continue

            text = ''
            for f in o.scared_of:
                if f != 'player':
                    text += f + '\n'
            surf = text_functions.speech_bubble(text, 300)
            pos = (o.coord[0] + o.dimensions[0], o.coord[1] - surf.get_height())
            self.world_objects_to_draw.append((surf, pos))

    def show_fear_ranges(self):
        for o in self.objects.itervalues():
            if isinstance(o, player.Player):
                r = o.fear_collection_radius
                surf = graphics.draw_circle(r, (64, 224, 208), 4)
                pos = (o.coord[0] + o.dimensions[0]/2 - r, o.coord[1] + o.dimensions[0]/2 - r)
                self.world_objects_to_draw.append((surf, pos))
            else:
                r = o.fear_radius
                surf = graphics.draw_circle(r, (75, 0, 130), 4)
                pos = (o.coord[0] + o.dimensions[0]/2 - r, o.coord[1] + o.dimensions[0]/2 - r)
                self.world_objects_to_draw.append((surf, pos))

    def change_map(self):
        self.map_index += 1
        self.map_index %= len(self.map_list)
        self.map = self.map_list[self.map_index]
        self.objects = dict(self.players.items() + self.map.objects.items())
        self.graphics.clip_area = pygame.Rect((0, 0), (self.dimensions[0], self.dimensions[1]))

    def set_state(self, state):
        self.GameState = state

    def quit_game(self):
        self.game_running = False

    def save_options(self):
        f = open(OPTIONS_FILE, 'w')
        for option, val in self.options.iteritems():
            f.write(option + ';' + str(val) + '~' + str(type(val)) + '\n')
        f.close()

    def load_options(self):
        f = open(OPTIONS_FILE, 'r')
        for l in f:
            semi = l.find(';')
            tilde = l.find('~')
            option = l[:semi]
            val = l[semi+1:tilde]
            typ = l[tilde+1:]
            typ = typ.rstrip()
            if typ == "<type 'bool'>":
                if val == 'True':
                    val = True
                else:
                    val = False
            elif typ == "<type 'int'>":
                val = int(val)
            elif typ == "<type 'float'>":
                val = float(val)

            self.options[option] = val
        f.close()

        self.options_menu.update_button_text_and_slider_values()
        self.options_menu.set_sound(self.options['sound_volume'])
        self.options_menu.set_music(self.options['music_volume'])
