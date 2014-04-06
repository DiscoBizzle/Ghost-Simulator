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
from gslib.constants import *
# doesn't seem to be needed any more
#if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:
#    # On NT like Windows versions smpeg video needs windb. --
#os.environ['SDL_VIDEODRIVER'] = ''

blackColour = pygame.Color(0, 0, 0)
blueColour = pygame.Color(0, 0, 255)

class Game(object):
    def __init__(self, width, height):
        self.Menu = menus.MainMenu(self)
        self.GameState = MAIN_MENU
        self.cutscene_started = False
        self.cutscene_next = os.path.join(VIDEO_DIR, "default.mpg")
        self.gameRunning = True
        self.dimensions = (width, height)
        self.graphics = graphics.Graphics(self)
        pygame.display.set_caption("Ghost Simulator v. 0.000000001a")
        self.music_list = sound.get_music_list()
        self.sound_dict = sound.load_all_sounds()
        self.credits = credits.Credits(self)
        self.options_menu = menus.OptionsMenu(self)

        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.fps_clock = pygame.time.Clock()

        self.camera_coords = (0, 0)

        self.objects = []

        self.players = []
        self.players.append(player.Player(self, 0, 0, 16, 16))
        self.players.append(player.Player(self, 0, 0, 16, 16))
        self.player1 = self.players[0]

        self.objects += self.players

        self.skills_dict = skills.load_skill_dict()
        self.SkillMenu = menus.SkillsMenu(self)

        # for i in range(5):
        #     self.objects.append(character.Character(self, 0, 0, 16, 16, character.gen_character()))

        self.text_box_test = text_box.TextBox("Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go. Mary had a little lamb whose fleece was white as snow and everywhere that mary went that lamb was sure to go.")

        self.text_box_test.create_background_surface()

        self.disp_object_stats = False
        self.object_stats = None

        self.options = {'FOV': True, 'VOF': False, 'torch': False}

        self.key_controller = key.KeyController(self)
        # HACK
        self.keys = self.key_controller.keys

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
        }

        #sound.start_next_music(self.music_list)

        self.map_list = []
        self.map_list.append(maps.Map(os.path.join(TILES_DIR, 'level2.png'), os.path.join(TILES_DIR, 'level2.json'), self))
        self.map_list.append(maps.Map(os.path.join(TILES_DIR, 'martin.png'), os.path.join(TILES_DIR, 'martin.json'), self))

        self.map_index = 0
        self.map = self.map_list[self.map_index]

        self.buttons = {}
        self.buttons['Possess'] = button.Button(self, self.possess, pos=(LEVEL_WIDTH, 0), size=(200, 30), visible=False,
                                                text=u'Possess', border_colour=(120, 50, 80), border_width=3,
                                                colour=(120, 0, 0), enabled=False)
        self.buttons['unPossess'] = button.Button(self, self.unPossess, pos=(LEVEL_WIDTH, 0), size=(200, 30), visible=False,
                                                text=u'Unpossess', border_colour=(120, 50, 80), border_width=3,
                                                colour=(120, 0, 0), enabled=False)

        self.buttons['change_map'] = button.Button(self, self.change_map, pos=(0, 0), size=(20, 20), visible=True,
                                                text=u'M', border_colour=(120, 50, 80), border_width=3,
                                                colour=(120, 0, 0), enabled=True)
        self.toPossess = None

        self.world_objects_to_draw = []
        self.screen_objects_to_draw = []
        self.objects += self.map.objects

        self.show_fears = False

    def gameLoop(self):
        while self.gameRunning:
            # Update clock & pump event queue.
            # We cannot do this at the same time as playing a cutscene on linux; pygame.movie is shite.
            if not (self.GameState == CUTSCENE and (
                        sys.platform == "linux2" or sys.platform == "linux" or sys.platform == "linux3")):
                self.clock.tick()
                self.msPassed += self.clock.get_time()

                for event in pygame.event.get():
                    response = self.event_map.get(event.type)
                    if response is not None:
                        response(event)

            if self.GameState == CUTSCENE:
                self.graphics.draw_cutscene()
                time.sleep(0.001)
            elif self.msPassed > 33:
                self.update()
                self.msPassed = 0

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

        if self.GameState == MAIN_GAME:
            for obj in self.objects:
                obj.update()
        elif self.GameState == CREDITS:
            self.credits.update()

    def calc_camera_coord(self):
        avg_pos = [0, 0]
        c = 0
        for p in self.players:
            c += 1
            avg_pos[0] += p.coord[0]
            avg_pos[1] += p.coord[1]

        avg_pos = (avg_pos[0] / c, avg_pos[1] / c)
        # coord = (self.player1.coord[0] - (GAME_WIDTH/2), self.player1.coord[1] - (GAME_HEIGHT/2))
        coord = (avg_pos[0] - (GAME_WIDTH/2), avg_pos[1] - (GAME_HEIGHT/2))
        pad = -32

        # bottom
        if coord[1] > (LEVEL_HEIGHT - GAME_HEIGHT) / 2 + pad:
            coord = (coord[0], (LEVEL_HEIGHT - GAME_HEIGHT) / 2 + pad)

        # right
        if coord[0] > (LEVEL_WIDTH - GAME_WIDTH)/2 - pad:
            coord = ((LEVEL_WIDTH - GAME_WIDTH)/2 - pad, coord[1])

        # left
        if coord[0] < pad:
            coord = (pad, coord[1])

        # top
        if coord[1] < pad:
            coord = (coord[0], pad)

        return coord

    def say_fears(self):
        for o in self.objects:
            if isinstance(o, player.Player):
                continue
            text = ''
            for f in o.scared_of:
                if f != 'player':
                    text += f + '\n'
            surf = fear_functions.speech_bubble(text, 300)
            pos = (o.coord[0] + o.dimensions[0], o.coord[1] - surf.get_height())
            self.world_objects_to_draw.append((surf, pos))

    def possess(self):
        self.toPossess.isPossessed = True
        self.player1.possessing = True

    def unPossess(self):
        self.toPossess.isPossessed = False
        self.player1.possessing = False
        self.player1.coord = self.toPossess.coord
        self.toPossess = None

    def change_map(self):
        self.map_index += 1
        self.map_index %= len(self.map_list)
        self.map = self.map_list[self.map_index]
        self.objects = self.players + self.map.objects

    def quit_game(self):
        self.gameRunning = False
