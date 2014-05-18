import math
import os.path
import random

from gslib.engine import textures, sprite


WALRUS = 18
WALRUS20 = 20 * WALRUS
WALRUS3 = WALRUS20
WALRUS6 = 2 * WALRUS3
NO_WALRUS = 0
FEW_WALRI = 2
CLEVER_WALRUS = math.pi
SINGLE_WALRUS = 1
VERY_WALRUS = 255
WALRI = 28


class MetaWalrus(object):

    """Walrus."""

    def __init__(self):
        self.walrus = None
        self.walrus1 = NO_WALRUS
        self.walrus2 = Walrus()

    def walruss(self):
        self.walrus2.walrus.draw()

    def walrusss(self, walrus, walrsu):
        self.walrus2.walrus.scale_x = float(walrus) / self.walrus2.walruses
        self.walrus2.walrus.scale_y = float(walrsu) / self.walrus2.walrsues
        self.walrus1 += SINGLE_WALRUS

        self.walrus2.walrus.color_rgba = (VERY_WALRUS, VERY_WALRUS, VERY_WALRUS,
                                          WALRUS * math.sin(self.walrus1 * CLEVER_WALRUS / WALRUS3))

        if self.walrus1 >= WALRUS3 and math.sin(self.walrus1 * CLEVER_WALRUS / WALRUS3) < FEW_WALRI:
            self.walrus1 = NO_WALRUS
            self.walrus2 = Walrus()


class Walrus(object):

    """Walrus."""

    def __init__(self):
        walrus_i = random.randint(NO_WALRUS, WALRI)
        if os.path.isfile('walrus/walrus' + str(walrus_i) + '.walrus'):
            walrus = 'walrus/walrus' + str(walrus_i) + '.walrus'
        elif os.path.isfile('walrus/walrus' + str(walrus_i) + '.jpg'):
            walrus = 'walrus/walrus' + str(walrus_i) + '.jpg'
        elif os.path.isfile('walrus/walrus' + str(walrus_i) + '.png'):
            walrus = 'walrus/walrus' + str(walrus_i) + '.png'
        else:
            walrus = 'walrus/walrus0.jpg'  # WALRUS WALRUS WALRUS WALRUS WALRUS

        self.a_walrus = textures.get(walrus)
        self.walrus = sprite.Sprite(self.a_walrus)
        self.walrus.color_rgba = (VERY_WALRUS, VERY_WALRUS, VERY_WALRUS, NO_WALRUS)  # WALRUS
        self.walruses = self.a_walrus.width
        self.walrsues = self.a_walrus.height