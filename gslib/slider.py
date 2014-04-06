import pygame


def create_property(var):  # creates a member variable that redraws the button when changed.
    def _setter(self, val):
        setattr(self, '_' + var, val)
        self.redraw()

    def _getter(self):
        return getattr(self, '_' + var)

    return property(_getter, _setter)


class Slider(object):
    def __init__(self, owner, func, pos=(0, 0), range=(0, 100), value=50, dim=(100, 20), back_colour=(255, 0, 0), fore_colour=(0, 255, 0)):
        self.owner = owner
        self.min, self.max = range
        self._value = value
        self._fore_colour = fore_colour
        self._back_colour = back_colour
        self.dim = dim
        self.pos = pos
        self.surface = None

        self.isClicked = False

        self.func = func

        self.redraw()

    def get_value(self):
        return self._value
    def set_value(self, val):
        self._value = val
        if self._value > self.max:
            self._value = self.max
        if self._value < self.min:
            self._value = self.min
        self.redraw()
    value = property(get_value, set_value)

    fore_colour = create_property('fore_colour')
    back_colour = create_property('back_colour')

    def redraw(self):
        surf = pygame.Surface(self.dim)
        surf.fill(self.back_colour)
        pygame.draw.rect(surf, self.fore_colour, pygame.Rect((0, 0), (self.dim[0] * (self.value - self.min) / float(self.max - self.min), self.dim[1])))
        self.surface = surf

    def check_clicked(self, event):
        click_pos = event.pos
        w, h = self.dim
        w /= 2
        h /= 2

        if event.type == pygame.MOUSEBUTTONUP:
            self.isClicked = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and abs(click_pos[0] - (self.pos[0] + w)) < w and abs(click_pos[1] - (self.pos[1] + h)) < h:
            self.isClicked = True

        if self.isClicked:
            frac = (click_pos[0] - self.pos[0]) / float(self.dim[0])
            self.value = self.min + (self.max - self.min) * frac
            self.func(self.value)

