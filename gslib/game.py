import os
import os.path
import sys
import time

import pyglet
#import pyglet.clock
#import pyglet.gl
#import pyglet.window
#from pygame import Rect
import pygame
import random

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
from gslib import character_functions
from gslib import text
from gslib import drop_down_list
from gslib import map_edit
from gslib import save_load
from gslib.constants import *


# doesn't seem to be needed any more
#if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:
#    # On NT like Windows versions smpeg video needs windb. --
#os.environ['SDL_VIDEODRIVER'] = ''
#os.environ['SDL_VIDEODRIVER'] = ''


class Game(pyglet.window.Window):
    """
    To draw something relative to map: (accounts for camera)
    game.world_objects_to_draw.append((surface, position))

    To draw something relative to game screen:
    game.screen_objects_to_draw.append((surface, position))

    Objects will be drawn without having to add them to these lists.
    """
    def __init__(self):
        super(Game, self).__init__(width=GAME_WIDTH, height=GAME_HEIGHT, resizable=True)

        TODO = []
        TODO.append("character pathe-ing")
        TODO.append("triggers/functions to handle move-to-position (after pathing)")
        TODO.append("click-to-edit text box - perhaps attached as a button function")
        TODO.append("then add character renaming/re-aging to map_edit (and able to edit speed by clicking the value")
        TODO.append("add deletion of function choices to char edit")
        TODO.append("add deletion of triggers to map edit")
        TODO.append("game_object.py set_colorkey pyglet port (use rgba spritesheet or write code to do magic)")
        TODO.append("create own Rect class for complete removal of pygame")
        TODO.append("implement pyglet camera")
        TODO.append("implement field of view slider (after pyglet camera implemented)")
        TODO.append("keybind menu in alphabetical order")
        TODO.append("add sound/music volume to options saving")
        TODO.append("design more sprites and make default characters (in character_objects)")
        TODO.append("add foreground layer to maps - then make characters appear *through* the foreground")
        TODO.append("add character save/load on a per-map basis (make sure triggers/funcs are preserved)")
        TODO.append("make it possible to cancel trigger creation")
        TODO.append("handle deletion of target of trigger")
        TODO.append("add more TODO's in __init__ of Game")

        self.TODO = TODO

        # enable alpha-blending
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.options = {'FOV': True, 'VOF': False, 'torch': False, 'menu_scale': False}
        self.dimensions = (GAME_WIDTH, GAME_HEIGHT)
        self.set_location(5, 30)  # aligns window to top left of screen (on windows atleast)

        self.Menu = menus.MainMenu(self, (161, 100))
        self.GameState = MAIN_MENU
        #self.GameState = MAIN_GAME
        self.cutscene_started = False
        self.cutscene_next = os.path.join(VIDEO_DIR, "default.mpg")
        self.game_running = True
        self.graphics = graphics.Graphics(self)
        self.set_caption("Ghost Simulator v. 0.000000001a")

        # TODO PYGLET

        self.sound_handler = sound.Sound()
        self.sound_handler.music_volume = 0.0
        self.sound_handler.start_next_music()

        self.credits = credits.Credits(self)
        self.options_menu = menus.OptionsMenu(self, (200, 50))
        self.fps_clock = pyglet.clock.ClockDisplay()

        self.camera_coords = (0, 0)
        self.camera_padding = (32, 32, 96, 32)  # left right up down

        self.players = {}
        self.players['player1'] = player.Player(self, TILE_SIZE*6, TILE_SIZE*2, 16, 16, 'GhostSheet.png')
        self.players['player2'] = player.Player(self, 0, 0, 16, 16, 'TutorialGhost2.png')

        # self.objects = dict(self.players.items())

        self.skills_dict = skills.load_skill_dict()
        self.SkillMenu = menus.SkillsMenu(self, (200,150))

        #self.text_box_test = text_box.TextBox("Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go.")

        #self.text_box_test.create_background_surface()

        self.disp_object_stats = False
        self.object_stats = None


        self.key_controller = key.KeyController(self)
        # # HACK
        # self.keys = self.key_controller.keys

        self.keybind_menu = menus.KeyBindMenu(self, (190, 40))
        self.action_to_rebind = None

        self.mouse_controller = mouse.MouseController(self)

        self.joy_controller = joy.JoyController(self)

        # self.event_map = {
        #     pygame.KEYDOWN: self.key_controller.handle_keys,
        #     pygame.KEYUP: self.key_controller.handle_keys,
        #     pygame.QUIT: (lambda _: self.quit_game()),
        #     # pygame.MOUSEBUTTONDOWN: self.mouse_controller.mouse_click,
        #     # pygame.MOUSEBUTTONUP: self.mouse_controller.mouse_up,
        #     # pygame.MOUSEMOTION: self.mouse_controller.mouse_move,
        #     pygame.VIDEORESIZE: self.graphics.resize_window,
        # }

        #sound.start_next_music(self.music_list)

        self.map_dict = {}
        self.map_dict['level3'] = save_load.load_map(self, 'level3')
        self.map_dict['level2'] = save_load.load_map(self, 'level2')
        self.map_dict['martin'] = save_load.load_map(self, 'martin')

        self.map_index = 'level3'
        self.map = self.map_dict[self.map_index]

        self.game_buttons = {
            'change_map': button.Button(self, self.change_map, pos=(0, 0), size=(20, 20), visible=True,
                                        text=u'M', border_colour=(120, 50, 80), border_width=3,
                                        colour=(120, 0, 0), enabled=True)}

        # self.toPossess = None
        self.selected_object = None

        self.world_objects_to_draw = []
        self.screen_objects_to_draw = []
        # self.objects = dict(self.objects.items() + self.map.objects.items())

        self.show_fears = False
        self.show_ranges = False

        # TODO PYGLET
        #self.load_options()
        self.key_controller.load()

        self.touching = []
        self.last_touching = []
        
        self.editor = map_edit.Editor(self)
        self.editor_active = False
        self.cursor = None
        self.new_trigger_capture = False

        self.game_drop_lists = {}

        self.buttons = {}
        self.drop_lists = {}
        self.objects = {}
        self.gather_buttons_and_drop_lists_and_objects()

        self.ticks_clock = pyglet.clock.Clock()
        self.ticks_clock_display = pyglet.clock.ClockDisplay(format='                 ticks:%(fps).2f',
                                                             clock=self.ticks_clock)
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    # pyglet event
    def on_key_press(self, symbol, modifiers):
        self.key_controller.keys.on_key_press(symbol, modifiers)
        self.key_controller.handle_keys(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.key_controller.keys.on_key_release(symbol, modifiers)
        self.key_controller.handle_keys(symbol, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_controller.mouse_move((x, y))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_controller.mouse_move((x, y))

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_controller.mouse_click((x, y), 'down', button)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_controller.mouse_click((x, y), 'up', button)

    # pyglet event
    def on_draw(self):
        #print "got to stupid fucking drawing"
        if self.game_running:
            if self.GameState == CUTSCENE:
                #print "cutscene"
                self.graphics.draw_cutscene()
            else:
                #print "not cutscene"
                self.graphics.main_game_draw()

            self.fps_clock.draw()
            self.ticks_clock_display.draw()

    def on_resize(self, width, height):
        self.dimensions = (width, height)
        pyglet.window.Window.on_resize(self, width, height)

    def gather_buttons_and_drop_lists_and_objects(self):
        self.buttons = dict(self.game_buttons.items())
        self.drop_lists = dict(self.game_drop_lists.items())

        if self.editor_active:
            self.drop_lists = dict(self.drop_lists.items() + self.editor.drop_lists.items())
            self.buttons = dict(self.buttons.items() + self.editor.buttons.items())


        self.objects = dict(self.players.items() + self.map.objects.items())
        if self.cursor:
            self.objects['cursor'] = self.cursor


    def update(self, dt):
        # this is fixed timestep, 30 FPS. if game runs slower, we lag.
        # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
        #self.objects.append(character.Character(self, 50, 50, 16, 16, character.gen_character()))
        self.ticks_clock.tick()
        self.camera_coords = self.calc_camera_coord()

        if self.GameState == MAIN_GAME:
            self.last_touching = [p for p in self.touching]  # creates a copy
            for obj in self.objects.itervalues():
                obj.update(dt)

            for i, p in enumerate(self.touching):
                if not p in self.last_touching:  # detect on touch
                    if p[0].has_touched_function:
                        for f in p[0].has_touched_function:
                            f(p[1])
                    if p[1].is_touched_function:
                        for f in p[1].is_touched_function:
                            f(p[0])

            for i, p in enumerate(self.last_touching):
                if not p in self.touching:  # detect on un-touch
                    if p[0].has_untouched_function:
                        for f in p[0].has_untouched_function:
                            f(p[1])
                    if p[1].is_untouched_function:
                        for f in p[1].is_untouched_function:
                            f(p[0])

        elif self.GameState == CREDITS:
            self.credits.update(dt)
        elif self.GameState == TEXTBOX_TEST:
            self.text_box_test.update(dt)

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

        pad = self.camera_padding

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
                surf = text.speech_bubble("Oonce oonce oonce oonce!", 200)
                pos = (o.coord[0] + o.dimensions[0], o.coord[1] - surf.get_height())
                self.world_objects_to_draw.append((surf, pos))
                continue

            message = ''
            for f in o.scared_of:
                if f != 'player':
                    message += f + '\n'
            surf = text.speech_bubble(message, 300)
            pos = (o.coord[0] + o.dimensions[0], o.coord[1] - surf.get_height())
            self.world_objects_to_draw.append((surf, pos))

    def show_fear_ranges(self):
        for o in self.objects.itervalues():
            if isinstance(o, player.Player):
                r = o.fear_collection_radius
                sprit = graphics.draw_circle(r, (64, 224, 208))
                sprit.set_position(o.coord[0] + o.sprite_width/2 - r, o.coord[1] + o.sprite_height/2 - r)
                self.world_objects_to_draw.append(sprit)
            else:
                r = o.fear_radius
                sprit = graphics.draw_circle(r, (75, 0, 130))
                sprit.set_position(o.coord[0] + o.dimensions[0]/2 - r, o.coord[1] + o.dimensions[0]/2 - r)
                self.world_objects_to_draw.append(sprit)

    def change_map(self):
        # self.map_index += 1
        # self.map_index %= len(self.map_list)
        self.map_index = random.choice(self.map_dict.keys())
        self.map = self.map_dict[self.map_index]
        # self.objects = dict(self.players.items() + self.map.objects.items())
        self.gather_buttons_and_drop_lists_and_objects()
        self.graphics.clip_area = pygame.Rect((0, 0), (self.dimensions[0], self.dimensions[1]))

    def set_state(self, state):
        self.GameState = state

    def quit_game(self):
        self.dispatch_event('on_close')

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
        # self.options_menu.set_sound(self.options['sound_volume'])
        # self.options_menu.set_music(self.options['music_volume'])
