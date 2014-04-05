import pygame
pygame.init()
import GameClass
import PlayerClass

Game = GameClass.Game(640, 480)

Game.gameLoop()

pygame.quit()
