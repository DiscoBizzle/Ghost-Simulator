import pygame


def create_property(var):  # creates a member variable that redraws the button when changed.
    def _setter(self, val):
        setattr(self, '_' + var, val)
        self.redraw()

    def _getter(self):
        return getattr(self, '_' + var)

    return property(_getter, _setter)


class Slider(object):
    def __init__(self, owner, pos=(0, 0), min_max=(0, 100), value=50, dim=(100, 20), back_colour=(255, 0, 0), fore_colour=(0, 255, 0)):
        self.owner = owner
        self.min, self.max = min_max
        self._value = value
        self._fore_colour = fore_colour
        self._back_colour = back_colour
        self.dim = dim
        self.pos = pos
        self.surface = None

        self.redraw()

    value = create_property('value')
    fore_colour = create_property('fore_colour')
    back_colour = create_property('back_colour')

    def redraw(self):
        surf = pygame.Surface(self.dim)
        surf.fill(self.back_colour)
        pygame.draw.Rect(surf, self.fore_colour, pygame.Rect((0, 0), (self.dim[0] * (self.value - self.min) / (self.max - self.min), self.dim[1])))
        self.surface = surf

    def check_clicked(self, click_pos):
        w, h = self.dim
        w /= 2
        h /= 2

        if abs(click_pos[0] - (self.pos[0] + w)) < w and abs(click_pos[1] - (self.pos[1] + h)) < h:
            frac = (click_pos[0] - self.pos[0]) / self.dim[0]
            self.value = self.min + (self.max - self.min) * frac

