import os
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
        self.cutscene_next = VIDEO_DIR + "default.mpg"
        self.gameRunning = True
        self.dimensions = (width, height)
        self.surface = pygame.display.set_mode(self.dimensions)
        self.music_list = sound.get_music_list()
        self.sound_dict = sound.load_all_sounds()
        self.credits = credits.Credits(self)
        self.options_menu = menus.OptionsMenu(self)


        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.fps_clock = pygame.time.Clock()

        self.camera_coords = (0, 0)

        self.objects = []

        self.player1 = player.Player(self, 0, 0, 16, 16)
        self.objects.append(self.player1)

        self.skills_dict = skills.load_skill_dict()
        self.SkillMenu = menus.SkillsMenu(self)


        # for i in range(5):
        #     self.objects.append(character.Character(self, 0, 0, 16, 16, character.gen_character()))

        self.disp_object_stats = False
        self.object_stats = None

        self.keys = {pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False,
                     pygame.K_ESCAPE: False, pygame.K_m: False, pygame.K_s: False}

        self.options = {'FOV': True, 'VOF': False, 'torch': False}
        field = pygame.image.load('tiles/field.png')
        field = pygame.transform.scale(field, (GAME_WIDTH, GAME_HEIGHT))
        field.set_alpha(100)
        field.convert_alpha()
        self.field = field

        light = pygame.image.load('light.png')
        light.convert_alpha()
        self.light = pygame.transform.scale(light, (200, 200))

        self.joy_controller = joy.JoyController(self)

        self.event_map = {
            pygame.KEYDOWN: self.handle_keys,
            pygame.KEYUP: self.handle_keys,
            pygame.QUIT: self.quit_game,
            pygame.MOUSEBUTTONDOWN: self.mouse_click,
            pygame.JOYHATMOTION: self.joy_controller.handle_hat,
            pygame.JOYBUTTONDOWN: self.joy_controller.handle_buttondown,
            pygame.JOYBUTTONUP: self.joy_controller.handle_buttonup,
            pygame.JOYAXISMOTION: self.joy_controller.handle_axis,
            pygame.JOYBALLMOTION: self.joy_controller.handle_ball,
        }

        #sound.start_next_music(self.music_list)

        self.map2 = maps.Map('tiles/martin.png', 'tiles/martin.json', self)
        self.map = maps.Map('tiles/level2.png', 'tiles/level2.json', self)

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
                graphics.draw_cutscene(self)
            elif self.msPassed > 33:
                self.update()
                self.msPassed = 0

                self.fps_clock.tick()
                self.main_game_draw()
            else:
                time.sleep(0.001)  # note: sleeping not only a good idea but necessary for pygame.movie os x

    def update(self):
        # this is fixed timestep, 30 FPS. if game runs slower, we lag.
        # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
        #self.objects.append(character.Character(self, 50, 50, 16, 16, character.gen_character()))

        self.camera_coords = self.calc_camera_coord()

        if self.GameState == MAIN_GAME:
            for obj in self.objects:
                obj.update()
        elif self.GameState == CREDITS:
            self.credits.update()

    def calc_camera_coord(self):
        coord = (self.player1.coord[0] - (GAME_WIDTH/2), self.player1.coord[1] - (GAME_HEIGHT/2))
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

    def main_game_draw(self):
        # this runs faster than game update. animation can be done here with no problems.

        if self.GameState != CUTSCENE:
            self.surface.fill(blackColour)

        if self.GameState == STARTUP:
            pass
        elif self.GameState == MAIN_MENU:
            self.Menu.display()
        elif self.GameState == MAIN_GAME:
            graphics.draw_map(self)
            graphics.draw_objects(self)
            if self.options['torch']:
                graphics.draw_torch(self)

            graphics.draw_buttons(self)

            graphics.draw_fear_bar(self)
            graphics.draw_fps(self)
            graphics.draw_character_stats(self)

        elif self.GameState == GAME_OVER:
            graphics.draw_game_over(self)

        elif self.GameState == CREDITS:
            self.credits.display()

        elif self.GameState == SKILLS_SCREEN:
            self.SkillMenu.display()
            
        elif self.GameState == OPTIONS_MENU:
            self.options_menu.display()

        if not self.options['FOV']:
            self.screen_objects_to_draw = []
            self.world_objects_to_draw = []

        graphics.draw_world_objects(self)
        graphics.draw_screen_objects(self)

        if self.options['VOF'] and self.GameState != CUTSCENE:
            self.surface.blit(self.field, (0, 0))

        pygame.display.update()

        # now double!
        # pygame.display.update()

    def handle_keys(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key in self.keys:
                self.keys[event.key] = True
        if event.type == pygame.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = False

        if self.keys[pygame.K_ESCAPE] and self.GameState != CUTSCENE:
            self.keys[pygame.K_ESCAPE] = False
            self.GameState = MAIN_MENU
        if self.keys[pygame.K_m]:
            self.keys[pygame.K_m] = False
            if self.GameState == MAIN_MENU or self.GameState == MAIN_GAME:
                self.GameState = CUTSCENE
        if self.keys[pygame.K_s] and (self.GameState == MAIN_MENU or self.GameState == MAIN_GAME):
            self.GameState = SKILLS_SCREEN

    def mouse_click(self, event):
        if self.GameState == MAIN_MENU:
            self.Menu.mouse_event(event)
        elif self.GameState == MAIN_GAME:
            self.check_button_click(event)
            self.check_object_click(event)
        elif self.GameState == SKILLS_SCREEN:
            self.SkillMenu.mouse_event(event)
        elif self.GameState == OPTIONS_MENU:
            self.options_menu.mouse_event(event)

    def check_object_click(self, event):
        if event.pos[0] > LEVEL_WIDTH or event.pos[1] > LEVEL_HEIGHT: # make track camera
            return
        for o in self.objects:
            st = SELECTION_TOLERANCE
            temp_rect = pygame.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
            if temp_rect.collidepoint((event.pos[0]+self.camera_coords[0],event.pos[1]+self.camera_coords[1])) and isinstance(o, character.Character):
                self.disp_object_stats = True
                self.object_stats = (o.info_sheet, (GAME_WIDTH - o.info_sheet.get_width(), 0))
                if self.player1.possessing:
                    return
                self.toPossess = o
                self.buttons['Possess'].visible = True
                # self.buttons['Possess'].enabled = True
                self.buttons['Possess'].pos = (GAME_WIDTH - o.info_sheet.get_width(), o.info_sheet.get_height())
                self.buttons['unPossess'].pos = (GAME_WIDTH - o.info_sheet.get_width(), o.info_sheet.get_height())
                return
        self.disp_object_stats = False
        self.object_stats = None
        self.buttons['Possess'].visible = False
        self.buttons['Possess'].enabled = False

    def check_button_click(self, event):
        for button in self.buttons.itervalues():
            button.check_clicked(event.pos)

        if self.player1.possessing:
            self.buttons['Possess'].visible = False
            self.buttons['Possess'].enabled = False
            self.buttons['unPossess'].visible = True
            self.buttons['unPossess'].enabled = True
        else:
            self.buttons['Possess'].visible = True
            self.buttons['Possess'].enabled = True
            self.buttons['unPossess'].visible = False
            self.buttons['unPossess'].enabled = False

    def possess(self):
        self.toPossess.isPossessed = True
        self.player1.possessing = True

    def unPossess(self):
        self.toPossess.isPossessed = False
        self.player1.possessing = False
        self.player1.coord = self.toPossess.coord
        self.toPossess = None

    def change_map(self):
        self.map, self.map2 = self.map2, self.map
        self.objects = [self.player1] + self.map.objects

    def quit_game(self, _):
        self.gameRunning = False
