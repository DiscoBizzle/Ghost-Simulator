import collections

import pygame

from gslib.constants import *

def parse_credits_file(fname):
    res = collections.defaultdict(list)
    with open(fname) as f:
        for line in f:
            key, names = line.split(":", 1)
            names = [n.strip() for n in names.split(",")]
            res[key].extend(names)
    return res

def get_credits_size(game, credits):
    lines = 0
    for k, v in credits.iteritems():
        pass
    return (0,0)

class Credits(object):
    def __init__(self, game):
        self.credits = parse_credits_file("credits.txt")
        self.GameClass = game
        self.surface = pygame.Surface(get_credits_size(game, self.credits))

    def display(self):
        self.GameClass.surface.fill((0, 0, 0))
