import pygame
import PlayerClass
from Constants import *

blackColour = pygame.Color(0, 0, 0)
blueColour = pygame.Color(0, 0, 255)

class Game:
    def __init__(self, windowWidth, windowHeight):
        self.GameState = MAIN_GAME
        self.gameRunning = True
        self.winDimensions = (windowWidth, windowHeight)
        self.windowSurface = pygame.display.set_mode(self.winDimensions)

        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.player1 = PlayerClass.Player(100,100,20,20)

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
        self.player1.update()

    def draw(self):
        # this runs faster than game update. animation can be done here with no problems.
        self.windowSurface.fill(blackColour)
        temp_surf = pygame.Surface((40, 40))

        pygame.draw.circle(temp_surf, blueColour, (20, 20), 20, 0)
        self.windowSurface.blit(temp_surf, self.player1.coord)
        pygame.display.update()

    def handleInput(self, event):
        if event.type == pygame.QUIT:
            self.gameRunning = False  # close the window, foo

        # Setting velocity is OK here, but you can't do any real physics in handleInput().
        # Do not do anything framerate-dependent in this function.

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.player1.velocity = (self.player1.velocity[0],-5)
            elif event.key == pygame.K_RIGHT:
                self.player1.velocity = (5,self.player1.velocity[1])
            elif event.key == pygame.K_LEFT:
                self.player1.velocity = (-5,self.player1.velocity[1])
            elif event.key == pygame.K_DOWN:
                self.player1.velocity = (self.player1.velocity[0],5)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                if self.player1.velocity[1] < 0:
                    self.player1.velocity = (self.player1.velocity[0],0)
            elif event.key == pygame.K_RIGHT:
                if self.player1.velocity[0] > 0:
                    self.player1.velocity = (0,self.player1.velocity[1])
            elif event.key == pygame.K_LEFT:
                if self.player1.velocity[0] < 0:
                    self.player1.velocity = (0,self.player1.velocity[1])
            elif event.key == pygame.K_DOWN:
                if self.player1.velocity[1] > 0:
                    self.player1.velocity = (self.player1.velocity[0],0)
