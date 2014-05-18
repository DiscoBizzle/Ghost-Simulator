from __future__ import absolute_import, division, print_function


# Static objects automatically created from touching mid layer sprites.
from gslib.engine import sprite, rect


class StaticObject(object):

    def __init__(self, x, y, w, h, texture):
        self.rect = rect.Rect((x, y), (w, h))
        self.sprite = sprite.Sprite(texture, x=x, y=y)
        self.coord = (x, y)
        self.flair = {}
