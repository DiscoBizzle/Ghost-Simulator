import collections

import pygame

from gslib.constants import *

def parse_credits_file(fname):
    """Build up a credits dictionary from a text file.

    The items in a credits dictionary are of the form 'job': ['person1', 'person2'].
    The text file format has one item per line, with the job separated
    from a comma-separated list of people by a colon.
    """
    res = collections.defaultdict(list)
    with open(fname) as f:
        for line in f:
            key, names = line.split(":", 1)
            names = [n.strip() for n in names.split(",")]
            res[key].extend(names)
    return res

def get_credits_size(credits, font, indent, spacing):
    """Calculate the size required for the credits."""
    if indent < 0:
        indent = -indent
    width, height = (0, 0)

    for k, v in credits.iteritems():
        # compute the size required for the header
        size = font.size(k)
        width = max(width, size[0])
        height += size[1]

        for name in v:
            size = font.size(name)
            width = max(width, size[0] + indent)
            height += size[1]

        height += spacing

    return (width, height)

class Credits(object):
    def __init__(self, game, indent=20, title_col=(255, 255, 255),
            name_col=(255, 255, 255), bg_col=(0, 0, 0), spacing=20, size=14):
        self.credits = parse_credits_file("credits.txt")
        self.GameClass = game
        self.indent = indent
        self.title_col = title_col
        self.name_col = name_col
        self.bg_col = bg_col
        self.spacing = spacing
        self.font = pygame.font.SysFont("helvetica", size)
        self.surface = pygame.Surface(get_credits_size(self.credits, self.font, self.indent, self.spacing))

    def display(self):
        height = 0
        for k, v in self.credits.iteritems():
            header = self.font.render(k, True, self.title_col, self.bg_col)
            if self.indent < 0:
                self.surface.blit(header, (self.indent, height))
            else:
                self.surface.blit(header, (0, height))
            height += header.get_height()

            for n in v:
                name = self.font.render(n, True, self.name_col, self.bg_col)
                if self.indent < 0:
                    self.surface.blit(name, (0, height))
                else:
                    self.surface.blit(name, (self.indent, height))
                height += header.get_height()

            height += self.spacing

        self.GameClass.surface.fill((0, 0, 0))

        margin = (self.GameClass.surface.get_width() - self.surface.get_width())/4
        height = self.GameClass.surface.get_height()

        self.GameClass.surface.blit(self.surface, (margin, height))
