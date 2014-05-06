from gslib import rect
from gslib import sprite


# Static objects automatically created from touching mid layer sprites.


class StaticObject(object):

    def __init__(self, x, y, w, h, texture):
        self.rect = rect.Rect((x, y), (w, h))
        self.sprite = sprite.Sprite(texture, x=x, y=y)
        self.coord = (x, y)
        self.flair = {}
