import pygame
import PlayerClass
from Constants import *

blackColour = pygame.Color(0, 0, 0)
blueColour = pygame.Color(0, 0, 255)

class Game:
    def __init__(self, windowWidth, windowHeight):
        self.GameState = MAIN_GAME
        self.gameRunning = True
        self.winDimensions = (windowWidth,windowHeight)
        self.windowSurface = pygame.display.set_mode(self.winDimensions)

        self.player1 = PlayerClass.Player(100,100,20,20)


    def gameLoop(self):
        while self.gameRunning:
            if self.GameState == STARTUP:
                pass
            elif self.GameState == MAIN_MENU:
                pass
            elif self.GameState == MAIN_GAME:
                #handleinput
                self.handleInput()
                #update stuff
                self.player1.update()
                #draw
                self.windowSurface.fill(blackColour)
                pygame.draw.circle(self.windowSurface, blueColour, self.player1.coord, 20, 0)
                pygame.display.update()


    def handleInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameRunning = False  # close the window, foo
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
