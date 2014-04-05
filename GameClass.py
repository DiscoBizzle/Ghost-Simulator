import pygame
import PlayerClass
from Constants import *

blackColour = pygame.Color(0, 0, 0)
blueColour = pygame.Color(0, 0, 255)

class Game:
    def __init__(self, width, height):
        self.GameState = MAIN_GAME
        self.gameRunning = True
        self.dimensions = (width, height)
        self.surface = pygame.Surface(self.dimensions)
        self.doublingSurface = pygame.display.set_mode((self.dimensions[0] * 2, self.dimensions[1] * 2))

        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.player1 = PlayerClass.Player(100,100,20,20)

        self.keys = { pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False }

    def gameLoop(self):
        while self.gameRunning:
            if self.GameState == STARTUP:
                pass
            elif self.GameState == MAIN_MENU:
                pass
            elif self.GameState == MAIN_GAME:
                self.clock.tick()
                self.msPassed += self.clock.get_time()

                # poll event queue
                for event in pygame.event.get():
                    if (event.type == pygame.KEYDOWN) or (event.type == pygame.KEYUP):
                        self.handleInput(event)
                    elif event.type == pygame.QUIT:
                        self.gameRunning = False

                if self.msPassed > 30:
                    self.update()
                    self.msPassed = 0

                self.draw()


    def update(self):
        # this is fixed timestep, 30 FPS. if game runs slower, we lag.
        # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
        self.player1.update(self)

    def draw(self):
        # this runs faster than game update. animation can be done here with no problems.
        self.surface.fill(blackColour)
        temp_surf = pygame.Surface((40, 40))

        pygame.draw.circle(temp_surf, blueColour, (20, 20), 20, 0)
        self.surface.blit(temp_surf, self.player1.coord)

        # now double!
        pygame.transform.scale(self.surface, (self.dimensions[0] * 2, self.dimensions[1] * 2), self.doublingSurface)
        pygame.display.update()

    def handleInput(self, event):
        if event.type == pygame.QUIT:
            self.gameRunning = False  # close the window, foo

        if event.type == pygame.KEYDOWN:
            if event.key in self.keys:
                self.keys[event.key] = True
        if event.type == pygame.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = False

