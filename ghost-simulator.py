#!/usr/bin/env python

import pygame

from gslib import game
from gslib.constants import *


def main():
    pygame.init()

    g = game.Game()
    g.game_loop()

    pygame.quit()


if __name__ == '__main__':
    main()
