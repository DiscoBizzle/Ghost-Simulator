import sys
import os

import pygame
import time

from gslib import player
from gslib import menus
from gslib import maps
from gslib import character
from gslib import graphics
from gslib import sound
from gslib import joy
from gslib import button
from gslib.constants import *
# doesn't seem to be needed any more
#if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:
#    # On NT like Windows versions smpeg video needs windb. --
#os.environ['SDL_VIDEODRIVER'] = ''

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

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
        #self.sound_dict = sound.load_all_sounds()

        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.fps_clock = pygame.time.Clock()

        self.camera_coords = (0, 0)

        self.objects = []

        self.player1 = player.Player(self, 0, 0, 16, 16)
        self.objects.append(self.player1)

        for i in range(5):
            self.objects.append(character.Character(self, 0, 0, 16, 16, character.gen_character()))

        self.disp_object_stats = False
        self.object_stats = None

        self.keys = {pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False,
                     pygame.K_ESCAPE: False, pygame.K_m: False}

        self.options = {'FOV': True, 'VOF': False}
        field = pygame.image.load('tiles/field.png')
        field = pygame.transform.scale(field, (GAME_WIDTH, GAME_HEIGHT))
        field.convert_alpha()
        field.set_alpha(100)
        self.field = field

        joy.init_joys()

        self.event_map = {
            pygame.KEYDOWN: self.handle_keys,
            pygame.KEYUP: self.handle_keys,
            pygame.QUIT: self.quit_game,
            pygame.MOUSEBUTTONDOWN: self.mouse_click,
            pygame.JOYHATMOTION: (lambda event: joy.handle_joy(self, event)),
            pygame.JOYBUTTONUP: (lambda event: joy.handle_joy(self, event)),
            pygame.JOYAXISMOTION: (lambda event: joy.handle_joy(self, event)),
            pygame.JOYBUTTONDOWN: (lambda event: joy.handle_joy(self, event)),
            pygame.JOYBALLMOTION: (lambda event: joy.handle_joy(self, event)),
        }

        sound.start_next_music(self.music_list)

        self.map = maps.Map('tiles/martin.png', 'tiles/martin.json')

        self.buttons = {}
        self.buttons['Possess'] = button.Button(self, self.possess, pos=(LEVEL_WIDTH, 0), size=(200, 30), visible=False,
                                                text='Possess', border_colour=(120, 50, 80), border_width=3,
                                                colour=(120, 0, 0), enabled=False)
        self.buttons['unPossess'] = button.Button(self, self.unPossess, pos=(LEVEL_WIDTH, 0), size=(200, 30), visible=False,
                                                text='Unpossess', border_colour=(120, 50, 80), border_width=3,
                                                colour=(120, 0, 0), enabled=False)
        self.toPossess = None

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

            if self.keys[pygame.K_ESCAPE] and self.GameState != CUTSCENE:
                self.keys[pygame.K_ESCAPE] = False
                self.GameState = MAIN_MENU
            if self.keys[pygame.K_m]:
                self.keys[pygame.K_ESCAPE] = False
                self.GameState = CUTSCENE

            if self.GameState == STARTUP:
                pass
            elif self.GameState == MAIN_MENU:
                pass
            elif self.GameState == MAIN_GAME:
                pass
            elif self.GameState == CUTSCENE:
                if self.cutscene_started:
                    if not movie.get_busy():
                        self.GameState = MAIN_GAME
                        self.cutscene_started = False
                        self.clock.get_time()  # hack required for pygame.movie linux
                        del movie  # hack required for pygame.movie mac os x
                else:
                    self.surface.fill(blackColour)
                    pygame.display.update()
                    try:
                        f = BytesIO(open(self.cutscene_next, "rb").read())
                        movie = pygame.movie.Movie(f)
                        w, h = movie.get_size()
                        movie.play()
                        self.cutscene_started = True
                    except IOError:
                        print "Video not found: " + self.cutscene_next
                        self.GameState = MAIN_MENU

            if self.GameState != CUTSCENE and self.msPassed > 33:
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
        if self.GameState == MAIN_GAME:
            for object in self.objects:
                object.update()

    def main_game_draw(self):
        # this runs faster than game update. animation can be done here with no problems.

        if self.GameState != CUTSCENE:
            self.surface.fill(blackColour)

        if self.GameState == STARTUP:
            pass
        elif self.GameState == MAIN_MENU:
            self.Menu.display()
        elif self.GameState == MAIN_GAME:
            if self.options['FOV']:
                self.surface.blit(graphics.draw_map(self.map), (0, 0))
                self.objects.sort((lambda x, y: cmp(x.coord[1], y.coord[1])))
                for o in self.objects:
                    if o == self.player1:
                        if o.possessing:
                            continue
                    self.surface.blit(o.sprite_sheet, (
                    o.coord[0] + o.dimensions[0] - SPRITE_WIDTH, o.coord[1] + o.dimensions[1] - SPRITE_HEIGHT),
                                      o.frame_rect)

                for button in self.buttons.itervalues():
                    self.surface.blit(button.surface, button.pos)

                font = pygame.font.SysFont('helvetica', 20)
                size = font.size("FEAR")
                fear_txt = font.render("FEAR", True, (200, 200, 200))
                self.surface.blit(fear_txt, (0, self.dimensions[1] - 32))
                fear_bar = pygame.Surface((self.dimensions[0] * self.player1.fear / MAX_FEAR, 32))
                fear_bar.fill((255, 0, 0))
                self.surface.blit(fear_bar, (size[0], self.dimensions[1] - 32))

                self.surface.blit(font.render('FPS: ' + str(int(self.fps_clock.get_fps())), True, (255, 255, 0)),
                                  (0, self.dimensions[1] - 100))

                if self.disp_object_stats:
                    self.surface.blit(self.object_stats[0], self.object_stats[1])
        elif self.GameState == GAME_OVER:
            font = pygame.font.SysFont('helvetica', 80)
            size = font.size("GAME OVER")
            margin = (self.dimensions[0] - size[0]) / 2
            self.surface.blit(font.render("GAME OVER", True, (255, 255, 255)), (margin, 100))
            font = pygame.font.SysFont('helvetica', 20)
            size = font.size("press esc scrub")
            margin = (self.dimensions[0] - size[0]) / 2
            self.surface.blit(font.render("press esc scrub", True, (255, 255, 255)), (margin, 200))

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

    def mouse_click(self, event):
        if self.GameState == MAIN_MENU:
            self.Menu.mouse_event(event)
        elif self.GameState == MAIN_GAME:
            self.check_button_click(event)
            self.check_object_click(event)

    def check_object_click(self, event):
        if event.pos[0] > LEVEL_WIDTH or event.pos[1] > LEVEL_HEIGHT:
            return
        for o in self.objects:
            st = SELECTION_TOLERANCE
            temp_rect = pygame.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
            if temp_rect.collidepoint(event.pos) and isinstance(o, character.Character):
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

    def quit_game(self, _):
        self.gameRunning = False
