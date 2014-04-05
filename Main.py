import pygame
pygame.init()
import GameClass
import PlayerClass
from Constants import *


def main():
    Game = GameClass.Game(GAME_WIDTH, GAME_HEIGHT)

    Game.gameLoop()

    pygame.quit()

if __name__ == '__main__': main()