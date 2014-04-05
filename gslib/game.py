import sys
import os

import pygame

from gslib import player
from gslib import menus
from gslib import maps
from gslib import character
from gslib import graphics
from gslib.constants import *
# doesn't seem to be needed any more
#if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:
#    # On NT like Windows versions smpeg video needs windb. -- 
#    os.environ['SDL_VIDEODRIVER'] = 'windib'

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

blackColour = pygame.Color(0, 0, 0)
blueColour = pygame.Color(0, 0, 255)

class Game:
    def __init__(self, width, height):
        self.Menu = menus.MainMenu(self)
        self.GameState = MAIN_MENU
        self.CutsceneStarted = False
        self.gameRunning = True
        self.dimensions = (width, height)
        self.surface = pygame.display.set_mode(self.dimensions)
        self.music_list = sound.get_music_list()
        #self.sound_dict = sound.load_all_sounds()

        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.cameraCoords = (0,0)

        self.player1 = player.Player(self, 100,100,SPRITE_WIDTH, SPRITE_HEIGHT)

        self.objects = [self.player1]

        for i in range(2):
            self.objects.append(character.Character(self, 50, 50, 16, 16, character.gen_character()))

        self.disp_object_stats = False
        self.object_stats = None

        self.keys = { pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_ESCAPE: False, pygame.K_m: False }

        self.options = {'FOV': True, 'VOF': False}
        field = pygame.image.load('field.png')
        field = pygame.transform.scale(field, (GAME_WIDTH, GAME_HEIGHT))
        field.convert_alpha()
        field.set_alpha(100)
        self.field = field

        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            joystick.init()

        self.event_map = {
            pygame.KEYDOWN: self.handle_keys,
            pygame.KEYUP: self.handle_keys,
            pygame.QUIT: self.quit_game,
            pygame.MOUSEBUTTONDOWN: self.mouse_click,
            pygame.JOYHATMOTION: self.handle_joy,
            pygame.MOUSEMOTION: self.mouse_motion,
        }

        self.map = maps.Map('tiles/martin.png', 'tiles/martin.json')
        sound.start_next_music(self.music_list)

        self.bees = -1

    def gameLoop(self):

        while self.gameRunning:
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
                self.clock.tick()
                self.msPassed += self.clock.get_time()
            elif self.GameState == CUTSCENE:
                if self.CutsceneStarted == True:
                    if not movie.get_busy():
                        self.GameState = MAIN_GAME
                        self.CutsceneStarted = False
                else:
                    
                    self.surface.fill(blackColour)
                    f = BytesIO(open("movie.mpg", "rb").read())
                    movie = pygame.movie.Movie(f)
                    w, h = movie.get_size()
                    
                    #screen = pygame.display.set_mode((w, h))
                    
                    movie.set_display(self.surface, pygame.Rect((5, 5), (w,h)))
                    
                    movie.play()
                    self.CutsceneStarted = True

            # poll event queue
            for event in pygame.event.get():
                response = self.event_map.get(event.type)
                if response is not None:
                    response(event)

            if self.msPassed > 30:
                self.update()
                self.msPassed = 0

            self.main_game_draw()

    def update(self):
        # this is fixed timestep, 30 FPS. if game runs slower, we lag.
        # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
        #self.objects.append(character.Character(self, 50, 50, 16, 16, character.gen_character()))
        for object in self.objects:
            object.update()

        if self.bees == -1 and self.player1.overFear:
            self.bees = 0
        if self.bees > -1:
            self.bees += 5
        if self.bees > 255:
            self.bees = 0

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
                for object in self.objects:
                    self.surface.blit(object.sprite, object.coord, object.frameRect)

                font = pygame.font.SysFont('helvetica', 20)
                size = font.size("FEAR")
                fear_txt = font.render("FEAR", True, (200, 200, 200))
                self.surface.blit(fear_txt, (0, self.dimensions[1]-32))
                fear_bar = pygame.Surface((self.dimensions[0]*self.player1.fear/MAX_FEAR, 32))
                fear_bar.fill((255, 0, 0))
                self.surface.blit(fear_bar, (size[0], self.dimensions[1]-32))

                if self.player1.overFear:
                    font2 = pygame.font.SysFont('helvetica', 64)
                    fg = font2.render("FEARGASM", 0, (200, self.bees, self.bees))
                    self.surface.blit(fg, ((GAME_WIDTH - fg.get_width()) / 2, (GAME_HEIGHT - fg.get_height()) / 2))

                self.surface.blit(font.render('FPS: ' + str(int(self.clock.get_fps())), True, (255, 255, 0)), (0, self.dimensions[1] - 100))

                if self.disp_object_stats:
                    self.surface.blit(self.object_stats[0], self.object_stats[1])

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

    def mouse_motion(self, event):
        for o in self.objects:
            if o.rect.collidepoint(event.pos) and isinstance(o, character.Character):
                self.disp_object_stats = True
                self.object_stats = (o.info_sheet, event.pos)
                return
        self.disp_object_stats = False
        self.object_stats = None

    def handle_joy(self, event):
        if event.type == pygame.JOYHATMOTION:
            x, y = event.value
            if x == -1:
                self.keys[pygame.K_LEFT] = True
            elif x == 1:
                self.keys[pygame.K_RIGHT] = True
            elif x == 0:
                self.keys[pygame.K_LEFT] = False
                self.keys[pygame.K_RIGHT] = False
            if y == -1:
                self.keys[pygame.K_DOWN] = True
            elif y == 1:
                self.keys[pygame.K_UP] = True
            elif y == 0:
                self.keys[pygame.K_DOWN] = False
                self.keys[pygame.K_UP] = False


    def quit_game(self, _):
        self.gameRunning = False
