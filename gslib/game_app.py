from __future__ import absolute_import, division, print_function

import pyglet
import random

from gslib import button
from gslib import collision
from gslib import credits
from gslib import graphics
from gslib import joy
from gslib import menus
from gslib import movie
from gslib import player
from gslib import skills
from gslib import sound
from gslib import key
from gslib import mouse
from gslib import text
from gslib import map_edit
from gslib import save_load
# from gslib import walrus
from gslib.rect import Rect
from gslib.constants import *
from gslib.class_proxy import Proxy
from gslib import options, window
import gslib


class Game(pyglet.event.EventDispatcher):
    """
    To draw something relative to map: (accounts for camera)
    game.world_objects_to_draw.append((surface, position))

    To draw something relative to game screen:
    game.screen_objects_to_draw.append((surface, position))

    Objects will be drawn without having to add them to these lists.
    """
    def __init__(self):

        Proxy.set_underlying_instance(gslib.game, self)

        TODO = []
        TODO.append("character pathe-ing")
        TODO.append("triggers/functions to start cutscene (both real loss-of-control and just as scripted movement")
        TODO.append("add new cutscenes to list without editing .json (easy! use InputBox!)")

        TODO.append("optimize map drawing: combine all sky layers, combine all ground layers")
        TODO.append("optimize map drawing: use just one texture for all mid layer static_objects")
        TODO.append("optimize map drawing: batch static_objects")

        TODO.append("add character renaming/re-aging to map_edit")

        TODO.append("implement pyglet camera (include zoom!)")
        TODO.append("implement field of view slider (after pyglet camera implemented)")

        TODO.append("keybind menu in alphabetical order")

        TODO.append("design more sprites and make default characters (in character_objects)")

        TODO.append("make it possible to cancel trigger creation")
        TODO.append("handle deletion of target of trigger")
        TODO.append("add deletion of function choices to char edit")
        TODO.append("add deletion of triggers to map edit")

        TODO.append("add idle_function to characters - wander, stand still, patrol (req. pathing)")

        TODO.append("drop list that appears if trigger action req. string argument")
        TODO.append("allow a zone to be chosen as a trigger target")

        TODO.append("add players to saving - both save_map and save_state")

        TODO.append("create decorator/thing to determine which properties to save")

        self.TODO = TODO

        # TODO: kill these attribs and make everything use the globals instead
        self.options = options
        self.window = window

        self.object_collision_lookup = collision.ObjectCollisionLookup(self)

        # enable alpha-blending
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.window.push_handlers(self)

        self.options.push_handlers(self)

        # TODO: why would we want this?
        #self.set_location(5, 30)  # aligns window to top left of screen (on windows atleast)

        self.main_menu = menus.MainMenu(self, (161, 100))
        self._state = STARTUP
        self.last_state = None
        self.movie_next = "default.mpg"
        self.movie_player = movie.MoviePlayer()
        self.game_running = True
        self.graphics = graphics.Graphics(self)
        self.window.set_caption("Ghost Simulator v. 0.000000001a")

        self.sound_handler = sound.Sound(self)

        self.credits = credits.Credits()
        self.options_menu = menus.OptionsMenu(self, (200, 50))

        self.camera_coords = (0, 0)
        self.camera_padding = (32, 32, 96, 32)  # left right up down

        self.players = {'player1': player.Player(self, TILE_SIZE * 6, TILE_SIZE * 2, 16, 16, 'GhostSheet.png'),
                        'player2': player.Player(self, 0, 0, 16, 16, 'TutorialGhost2.png')}

        self.skills_dict = skills.load_skill_dict()
        self.skill_menu = menus.SkillsMenu(self, (200, 150))

        #self.text_box_test = text_box.TextBox("Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go.")

        #self.text_box_test.create_background_surface()

        self.disp_object_stats = False
        self.object_stats = None

        # input controllers
        self.key_controller = key.KeyController(self)
        self.mouse_controller = mouse.MouseController(self)
        self.joy_controller = joy.JoyController(self)

        self.keybind_menu = menus.KeyBindMenu(self, (190, 40))
        self.action_to_rebind = None

        self.map = None

        self.map_dict = {'level3': save_load.load_map(self, 'level3'),
                         'level2': save_load.load_map(self, 'level2'),
                         'martin': save_load.load_map(self, 'martin')}

        self.map_index = 'level3'
        self.map = self.map_dict[self.map_index]

        self.game_buttons = {
            'change_map': button.Button(self, self.change_map, pos=(0, 0), size=(20, 20), visible=True,
                                        text=u'M', border_color=(120, 50, 80), border_width=3,
                                        color=(120, 0, 0), enabled=True)}

        # self.toPossess = None
        self.selected_object = None

        self.world_objects_to_draw = []
        self.screen_objects_to_draw = []
        # self.objects = dict(self.objects.items() + self.map.objects.items())

        self.show_fears = False
        self.show_ranges = False
        # self.walrus = walrus.MetaWalrus()

        self.key_controller.load()

        self.touching = []
        self.last_touching = []

        self.editor = map_edit.Editor(self)
        self.force_run_objects = False
        self.cursor = None
        self.new_trigger_capture = False

        self.game_drop_lists = {}

        self.buttons = {}
        self.drop_lists = {}
        self.objects = {}
        self.gather_buttons_and_drop_lists_and_objects()

        self.fps_clock = pyglet.clock.ClockDisplay()
        self.ticks_clock = pyglet.clock.Clock()
        self.ticks_clock_display = pyglet.clock.ClockDisplay(format='               ticks:%(fps).2f',
                                                             clock=self.ticks_clock)
        self.draw_clock = pyglet.clock.Clock()
        self.draw_clock_display = pyglet.clock.ClockDisplay(format='                                     fps:%(fps).2f',
                                                            clock=self.draw_clock)

        pyglet.clock.schedule_once(self.update, TICK_DELAY)
        self._last_update_delay = TICK_DELAY

        # improve timing (hack)
        self.scheduler_hint_fun = lambda dt: None
        pyglet.clock.schedule_interval(self.scheduler_hint_fun, 1.0 / self.options['scheduler_frequency'])

        self.sound_handler.play_music('2 ghost lane')

        self.message_box = None  # If set, a message box taking all focus is being displayed.
        self.text_caret = None   # If set, all keyboard input & copy of mouse events should be posted to this object.

        self.text_box = None  # If set, dialogue is being played.

        self.update_exception_hook = (None, None)

        self.state = MAIN_MENU

        self.fears_dict = self.map.fears_dict

    @property
    def dimensions(self):
        return self.window.get_size()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state == self._state:
            return
        self.last_state = self._state
        self._state = state
        self.dispatch_event('on_state_change', state)

    def update_scheduler_frequency(self):
        pyglet.clock.unschedule(self.scheduler_hint_fun)
        pyglet.clock.schedule_interval(self.scheduler_hint_fun, 1.0 / self.options['scheduler_frequency'])

    def on_state_change(self, state):
        # update menu enabled states
        self.main_menu.enabled = state == MAIN_MENU
        self.skill_menu.enabled = state == SKILLS_SCREEN
        self.options_menu.enabled = state == OPTIONS_MENU
        self.keybind_menu.enabled = state == KEYBIND_MENU or state == KEYBIND_CAPTURE
        if self.last_state == EDITOR:
            self.editor.exit_edit_mode()
        elif self.last_state == CREDITS:
            self.credits.remove_handlers(self)
        elif self.last_state == MOVIE:
            self.movie_player.remove_handlers(self)
        if state == MAIN_GAME:
            if self.sound_handler.music_playing is not None:
                if self.sound_handler.music_playing.name != 'transylvania':
                    self.sound_handler.play_music('transylvania')
        elif state == EDITOR:
            self.editor.enter_edit_mode()
        elif state == CREDITS:
            self.credits.push_handlers(self)
            self.credits.start()
        elif state == MOVIE:
            self.movie_player.push_handlers(self)
            self.movie_player.start(self.movie_next)

    def on_credits_end(self):
        self.state = MAIN_MENU

    def on_movie_end(self):
        self.state = self.last_state

    # pyglet event
    def on_draw(self):
        self.draw_clock.tick()

        self.graphics.main_game_draw()

        self.fps_clock.draw()
        #self.walrus.walruss()
        self.ticks_clock_display.draw()
        self.draw_clock_display.draw()

    def on_resize(self, width, height):
        self.update_camera()

    def gather_buttons_and_drop_lists_and_objects(self):
        self.buttons = dict(self.game_buttons.items())
        self.drop_lists = dict(self.game_drop_lists.items())

        self.objects = dict(self.players.items() + self.map.objects.items())
        if self.cursor:
            self.objects['cursor'] = self.cursor

        self.fears_dict = self.map.fears_dict

    def update(self, dt):
        # Calculate the next time to schedule the update call.
        # (dt - self._last_update_delay) is how late we were.
        # Schedule the next update to be TICK_DELAY minus how late we were last time
        # bound to be between 0 and TICK_DELAY so we don't schedule in the past or too far in the future
        next_delay = max(0, TICK_DELAY - max(0, (dt - self._last_update_delay)))
        pyglet.clock.schedule_once(self.update, next_delay)
        #print((dt, self._last_update_delay, next_delay))
        self._last_update_delay = next_delay
        try:
            # this is fixed timestep, 30 FPS. if game runs slower, we lag.
            # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
            #self.objects.append(character.Character(self, 50, 50, 16, 16, character.gen_character()))
            self.ticks_clock.tick()
            self.update_camera()
            #self.walrus.walrusss(self.dimensions[0], self.dimensions[1])

            if self.state == MAIN_GAME or self.state == EDITOR:

                self.last_touching = self.touching[:]  # creates a copy

                if self.map.active_cutscene is not None and not self.map.active_cutscene.done:
                    self.map.active_cutscene.update()

                self.object_collision_lookup.update_all()

                if self.state != EDITOR or self.force_run_objects:  # pause game while in edit mode
                    for obj in self.objects.itervalues():
                        obj.update(dt)

                for p in self.touching:
                    if not p in self.last_touching:  # detect on touch
                        if p[0].has_touched_function:
                            for f in p[0].has_touched_function:
                                f(p[1])
                        if p[1].is_touched_function:
                            for f in p[1].is_touched_function:
                                f(p[0])

                for p in self.last_touching:
                    if not p in self.touching:  # detect on un-touch
                        if p[0].has_untouched_function:
                            for f in p[0].has_untouched_function:
                                f(p[1])
                        if p[1].is_untouched_function:
                            for f in p[1].is_untouched_function:
                                f(p[0])

                if self.text_box is not None:
                    self.text_box.update()

                if self.state == EDITOR:
                    self.editor.update()

            elif self.state == CREDITS:
                self.credits.update(dt)

        except self.update_exception_hook[0] as exception:
            self.update_exception_hook[1](exception)

    def update_camera(self):
        avg_pos = [0, 0]
        c = 0
        for p in self.players.itervalues():
            c += 1
            avg_pos[0] += p.coord[0]
            avg_pos[1] += p.coord[1]

        avg_pos = (avg_pos[0] // c, avg_pos[1] // c)
        # coord = (self.player1.coord[0] - (self.dimensions[0]/2), self.player1.coord[1] - (self.dimensions[1]/2))
        coord = (avg_pos[0] - (self.dimensions[0] // 2), avg_pos[1] - (self.dimensions[1] // 2))

        pad = self.camera_padding

        # bottom
        if avg_pos[1] > LEVEL_HEIGHT - self.dimensions[1] // 2 + pad[3]:
            coord = (coord[0], LEVEL_HEIGHT - self.dimensions[1] + pad[3])

        # right
        if avg_pos[0] > LEVEL_WIDTH - self.dimensions[0] // 2 + pad[1]:
            coord = (LEVEL_WIDTH - self.dimensions[0] + pad[1], coord[1])

        # left
        if avg_pos[0] < self.dimensions[0] // 2 - pad[0] or LEVEL_WIDTH < self.dimensions[0] - pad[0] - pad[1]:
            coord = (-pad[0], coord[1])

        # top
        if avg_pos[1] < self.dimensions[1] // 2 - pad[2] or LEVEL_HEIGHT < self.dimensions[1] - pad[2] - pad[3]:
            coord = (coord[0], -pad[2])

        self.camera_coords = coord

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
                sprit.set_position(o.coord[0] + o.sprite_width // 2 - r, o.coord[1] + o.sprite_height // 2 - r)
                self.world_objects_to_draw.append(sprit)
            else:
                r = o.fear_radius
                sprit = graphics.draw_circle(r, (75, 0, 130))
                sprit.set_position(o.coord[0] + o.dimensions[0] // 2 - r, o.coord[1] + o.dimensions[0] // 2 - r)
                self.world_objects_to_draw.append(sprit)

    def change_map(self):
        self.map_index = random.choice(self.map_dict.keys())
        self.go_to_map(self.map_dict[self.map_index])

    def go_to_map(self, m):
        self.map = m
        self.gather_buttons_and_drop_lists_and_objects()
        self.graphics.clip_area = Rect((0, 0), (self.dimensions[0], self.dimensions[1]))
        self.fears_dict = self.map.fears_dict

    def run_cutscene(self, c):
        self.map.active_cutscene = c
        c.restart()

    def quit_game(self):
        self.window.dispatch_event('on_close')

Game.register_event_type('on_state_change')