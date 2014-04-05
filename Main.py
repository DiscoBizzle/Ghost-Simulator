import pygame
pygame.init()
import GameClass
import PlayerClass
from Constants import *

Game = GameClass.Game(WINDOW_WIDTH, WINDOW_HEIGHT)

Game.gameLoop()

pygame.quit()
