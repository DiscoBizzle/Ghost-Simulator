import pygame
pygame.init()
import GameClass
import PlayerClass
from Constants import *

Game = GameClass.Game(GAME_WIDTH, GAME_HEIGHT)

Game.gameLoop()

pygame.quit()
