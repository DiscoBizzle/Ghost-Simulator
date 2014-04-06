#!/usr/bin/env python

import pygame

from gslib import game
from gslib.constants import *


def main():
    pygame.init()

    Game = game.Game(GAME_WIDTH, GAME_HEIGHT)
    Game.gameLoop()

    pygame.quit()


if __name__ == '__main__':
    main()
