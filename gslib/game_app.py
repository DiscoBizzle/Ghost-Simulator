from __future__ import absolute_import, division, print_function

import random

import pyglet

from gslib import collision
from gslib import pathfinder
from gslib import skills
from gslib.editor.main_editor import Editor
from gslib import save_load
from gslib import walrus
from gslib.engine import mouse, key, graphics, movie, sound, joy, camera
from gslib.constants import *
from gslib.class_proxy import Proxy
from gslib import options, window
import gslib
from gslib.game_objects import player
from gslib.ui import button, credits, menus, game_over_screen
from gslib import maps


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
        TODO.append("character pathe-ing; then add a go_to function, include in idle_functions.patrol")

        TODO.append("optimize map drawing: combine all sky layers, combine all ground layers")
        TODO.append("optimize map drawing: use just one texture for all mid layer static_objects")
        TODO.append("optimize map drawing: batch static_objects")

        TODO.append("add character renaming/re-aging to map_edit")

        TODO.append("implement pyglet camera (include zoom!)")
        TODO.append("implement field of view slider (after pyglet camera implemented)")

        TODO.append("keybind menu in alphabetical order")

        TODO.append("design more sprites and make default characters (in character_objects)")

        TODO.append("add deletion of function choices to char edit - generally improve it")

        TODO.append("add players to saving - both save_map and save_state")

        TODO.append("better character function editor, specifically patrol path")

        TODO.append("activate() while possessed button")
        TODO.append("props that cant be possess-walked - can be picked up but cant pick up")
        TODO.append("chars that can pick props up - works in conjunction with flair (keep flair for particle effects)")

        self.TODO = TODO

        self.object_collision_lookup = collision.ObjectCollisionLookup(self)
        self.pathfinder = pathfinder.Pathfinder()

        self.camera_padding = (32, 32, 96, 32)  # left right up down
        self._zoom = 1.0
        self.camera = camera.Camera(x=0, y=0, zoom=self._zoom)

        # enable alpha-blending
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        window.push_handlers(self)

        options.push_handlers(self)

        # TODO: why would we want this?
        #self.set_location(5, 30)  # aligns window to top left of screen (on windows atleast)

        self.main_menu = menus.MainMenu(self, (161, 100))
        self._state = STARTUP
        self.last_state = None
        self.movie_next = "default.mpg"
        self.movie_player = movie.MoviePlayer()
        self.game_running = True
        self.graphics = graphics.Graphics(self)

        self.sound_handler = sound.Sound()

        self.credits = credits.Credits()
        self.options_menu = menus.OptionsMenu(self, (200, 50))

        self.game_over_screen = game_over_screen.GameOverScreen()

        self.players = {'player1': player.Player(self, TILE_SIZE * 6, TILE_SIZE * 2, 16, 16, 'GhostSheet.png'),
                        'player2': player.Player(self, 0, 0, 16, 16, 'TutorialGhost2.png')}

        self.skills_dict = skills.load_skill_dict()
        self.skill_menu = menus.SkillsMenu(self, (200, 150))

        self.disp_object_stats = False
        self.object_stats = None

        # input controllers
        self.key_controller = key.KeyController(self)
        self.mouse_controller = mouse.MouseController(self)
        self.joy_controller = joy.JoyController(self)

        self.keybind_menu = menus.KeyBindMenu(self, (190, 40))
        self.action_to_rebind = None

        self._map = None

        self.map_dict = {}

        # self.map_dict['level3'] = save_load.load_map(self, 'level3')
        # self.map_dict['level2'] = save_load.load_map(self, 'level2')
        # self.map_dict['martin'] = save_load.load_map(self, 'martin')
        # self.map_dict['boss1'] = save_load.load_map(self, 'boss1')
        self.map_dict['boss2'] = save_load.load_map(self, 'boss2')

        self.map_index = 'boss2'
        self.map = self.map_dict[self.map_index]

        self.game_buttons = {
            'change_map': button.Button(function=self.change_map, pos=(0, 0), size=(20, 20), visible=True, text=u'M',
                                        border_color=(120, 50, 80), border_width=3, color=(120, 0, 0), window=window)}

        self.game_drop_lists = {}

        # self.toPossess = None
        self.selected_object = None

        self.world_objects_to_draw = []
        self.screen_objects_to_draw = []
        # self.objects = dict(self.objects.items() + self.map.objects.items())

        self.show_fears = False
        self.show_ranges = False
        self.walrus = walrus.MetaWalrus()

        self.key_controller.load()

        self.touching = []
        self.last_touching = []

        self.editor = Editor(self)
        self.force_run_objects = False
        self.cursor = None
        self.new_trigger_capture = False

        self.objects = {}
        self.gather_objects()

        self.highlighted_control = ""

        self.fps_clock = pyglet.clock.ClockDisplay()
        self.ticks_clock = pyglet.clock.Clock()
        self.ticks_clock_display = pyglet.clock.ClockDisplay(format='               ticks:%(fps).2f',
                                                             clock=self.ticks_clock)
        self.draw_clock = pyglet.clock.Clock()
        self.draw_clock_display = pyglet.clock.ClockDisplay(format='                                     fps:%(fps).2f',
                                                            clock=self.draw_clock)

        pyglet.clock.schedule_interval(self.update, TICK_INTERVAL)

        self.sound_handler.play_music('2 ghost lane')

        self.message_box = None  # If set, a message box taking all focus is being displayed.

        self.dialogue = None  # If set, dialogue is being played.

        self.update_exception_hook = (None, None)

        self.state = MAIN_MENU

        self.fears_dict = self.map.fears_dict

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value == self._state:
            return
        self.last_state = self._state
        self._state = value
        self.dispatch_event('on_state_change', value)

    @property
    def map(self):
        return self._map

    @map.setter
    def map(self, value):
        if value == self._map:
            return
        self._map = value
        self.dispatch_event('on_map_change', value)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value < 0.1 or value == self._zoom:
            return
        self._zoom = value
        self.update_camera()

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
        elif self.last_state == GAME_OVER:
            self.game_over_screen.remove_handlers(self)
        elif self.last_state == MAIN_GAME:
            for but in self.game_buttons.itervalues():
                but.enabled = False
            if self.sound_handler.current_music != '2 ghost lane':
                self.sound_handler.play_music('2 ghost lane')
        if state == MAIN_GAME:
            for but in self.game_buttons.itervalues():
                but.enabled = True
            if self.sound_handler.current_music != 'transylvania':
                self.sound_handler.play_music('transylvania')
        elif state == EDITOR:
            self.editor.enter_edit_mode()
        elif state == CREDITS:
            self.credits.push_handlers(self)
            self.credits.start()
        elif state == MOVIE:
            self.movie_player.push_handlers(self)
            self.movie_player.start(self.movie_next)
        elif state == GAME_OVER:
            self.game_over_screen.push_handlers(self)
            self.game_over_screen.start()

    def on_credits_end(self):
        self.state = MAIN_MENU

    def on_movie_end(self):
        self.state = self.last_state

    def on_game_over_close(self):
        self.state = MAIN_MENU

    def on_draw(self):
        self.draw_clock.tick()

        if self.state == MAIN_GAME or self.state == EDITOR:
            self.graphics.main_game_draw()

        if options['VOF']:
            self.graphics.field.draw()

        if options['walrus']:
            self.walrus.walruss()

        if options['show_fps']:
            self.fps_clock.draw()
            self.ticks_clock_display.draw()
            self.draw_clock_display.draw()

    def on_resize(self, width, height):
        self.update_camera()

    def gather_objects(self):
        self.objects = {}
        self.objects.update(self.players)
        self.objects.update(self.map.objects)
        if self.cursor:
            self.objects['cursor'] = self.cursor

        self.fears_dict = self.map.fears_dict

    def update(self, dt):

        try:
            # this is fixed timestep, 30 FPS. if game runs slower, we lag.
            # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
            #self.objects.append(character.Character(self, 50, 50, 16, 16, character.gen_character()))
            self.ticks_clock.tick()
            if options['walrus']:
                self.walrus.walrusss(window.width, window.height)

            if self.state == MAIN_GAME or self.state == EDITOR:

                self.last_touching = self.touching[:]  # creates a copy
                del self.touching[:] # clears list

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
                                f.function(p[1])
                        if p[1].is_touched_function:
                            for f in p[1].is_touched_function:
                                f.function(p[0])

                for p in self.last_touching:
                    if not p in self.touching:  # detect on un-touch
                        if p[0].has_untouched_function:
                            for f in p[0].has_untouched_function:
                                f.function(p[1])
                        if p[1].is_untouched_function:
                            for f in p[1].is_untouched_function:
                                f.function(p[0])

                if self.dialogue is not None:
                    self.dialogue.update()

                if self.state == EDITOR:
                    self.editor.update()

                self.update_camera()

        except self.update_exception_hook[0] as exception:
            self.update_exception_hook[1](exception)

    def update_camera(self):
        """
        Update the camera's properties based on the players position and zoom level.
        This will try to keep as much of the map on screen as possible.
        If a player wnaders off screen it will zoom out to show them.
        """

        w = window.width
        h = window.height

        zoom = self.zoom

        player_xs, player_ys = zip(*(p.coord for p in self.players.itervalues()))

        # adjust zoom if maximum distance between players adjusted for zoom is greater than the window width
        # add TILE_SIZE so the whole player can stay in view
        diff_x = (max(player_xs) - min(player_xs)) + TILE_SIZE
        if diff_x * zoom > w:
            zoom = w / diff_x

        # adjust zoom if maximum distance between players adjusted for zoom is greater than the window height
        # add TILE_SIZE so the whole player can stay in view
        diff_y = (max(player_ys) - min(player_ys)) + TILE_SIZE
        if diff_y * zoom > h:
            zoom = h / diff_y

        # calculate the average position of all players
        avg_x = reduce(lambda total, p: total + p, player_xs, 0) / len(player_xs)
        avg_y = reduce(lambda total, p: total + p, player_ys, 0) / len(player_ys)

        # account for zoom level
        avg_x *= zoom
        avg_y *= zoom
        level_width = LEVEL_WIDTH * zoom
        level_height = LEVEL_HEIGHT * zoom

        pad_left, pad_right, pad_top, pad_bottom = (p * zoom for p in self.camera_padding)

        if pad_left + level_width + pad_right < w:
            # level fits in window so center it
            x = (level_width - w) / 2
        elif avg_x < w / 2 - pad_left:
            # close to left edge
            x = -pad_left
        elif avg_x > level_width - w / 2 + pad_right:
            # close to right edge
            x = level_width - w + pad_right
        else:
            # center on avg_x
            x = avg_x - (w / 2)

        if pad_bottom + level_height + pad_top < h:
            # level fits in window so center it
            y = (level_height - h) / 2
        elif avg_y < h / 2 - pad_top:
            # close to top edge
            y = -pad_top
        elif avg_y > level_height - h / 2 + pad_bottom:
            # close to bottom edge
            y = level_height - h + pad_bottom
        else:
            # center on avg_y
            y = avg_y - (h / 2)

        self.camera.x = int(x)
        self.camera.y = int(y)
        self.camera.zoom = zoom

    def change_map(self):
        self.map_index = random.choice(self.map_dict.keys())
        self.go_to_map(self.map_dict[self.map_index])

    def go_to_map(self, m):
        if isinstance(m, maps.Map):
            _map = m
        else:  # accept map name/index
            if m in self.map_dict.values():
                _map = self.map_dict[m]
            else:
                _map = save_load.load_map(self, m)
                self.map_dict[m] = _map

        self.map = _map
        self.gather_objects()
        self.fears_dict = self.map.fears_dict

    def run_cutscene(self, c):
        self.map.active_cutscene = c
        c.restart()

    def find_objects_within_range(self, obj, rang):
        r_squared = rang**2
        objs_within_range = []
        for o in self.objects.itervalues():
            if o == obj:
                continue
            d = (obj.coord[0] - o.coord[0])**2 + (obj.coord[1] - o.coord[1])**2
            if d < r_squared:
                objs_within_range.append(o)

        return objs_within_range

    @staticmethod
    def quit_game():
        window.dispatch_event('on_close')

Game.register_event_type('on_state_change')
Game.register_event_type('on_map_change')
