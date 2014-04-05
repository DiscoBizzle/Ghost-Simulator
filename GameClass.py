import pygame
import PlayerClass
from Constants import *
import Menus

blackColour = pygame.Color(0, 0, 0)
blueColour = pygame.Color(0, 0, 255)

class Game:
    def __init__(self, width, height):
        self.Menu = Menus.MainMenu(self)
        self.GameState = MAIN_MENU
        self.gameRunning = True
        self.dimensions = (width, height)
        self.surface = pygame.display.set_mode(self.dimensions)

        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.cameraCoords = (0,0)

        self.player1 = PlayerClass.Player(100,100,40,40)

        self.keys = { pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_ESCAPE: False}

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
            pygame.JOYHATMOTION: self.handle_joy
        }

    def gameLoop(self):
        VOF_counter = 0
        while self.gameRunning:
            if self.keys[pygame.K_ESCAPE]:
                self.keys[pygame.K_ESCAPE] = False
                self.GameState = MAIN_MENU
            if self.GameState == STARTUP:
                pass
            elif self.GameState == MAIN_MENU:
                pass
            elif self.GameState == MAIN_GAME:
                self.clock.tick()
                self.msPassed += self.clock.get_time()

            # poll event queue
            for event in pygame.event.get():
                response = self.event_map.get(event.type)
                if response is not None:
                    response(event)

            if self.msPassed > 30:
                self.update()
                self.msPassed = 0


            self.surface.fill(blackColour)

            if self.GameState == STARTUP:
                pass
            elif self.GameState == MAIN_MENU:
                self.Menu.display()
            elif self.GameState == MAIN_GAME:
                if not self.options['FOV']:
                    self.surface.fill(blackColour)
                    pygame.display.update()
                else:
                    self.main_game_draw()

            if self.options['VOF']:
                self.surface.blit(self.field, (0, 0))
            pygame.display.update()


    def update(self):
        # this is fixed timestep, 30 FPS. if game runs slower, we lag.
        # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
        self.player1.update(self)

    def main_game_draw(self):
        # this runs faster than game update. animation can be done here with no problems.
        # self.surface.fill(blackColour)
        temp_surf = pygame.Surface((40, 40))

        pygame.draw.circle(temp_surf, blueColour, (20, 20), 20, 0)

        self.surface.blit(self.player1.spriteSheet, self.player1.coord, self.player1.frameRect)

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
