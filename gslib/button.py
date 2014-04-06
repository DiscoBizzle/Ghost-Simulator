import pygame


def valid_colour(colour):
    for i in colour:
        if i < 0 or i > 255:
            return 0
    return 1


def create_property(var):  # creates a member variable that redraws the button when changed.
    def _setter(self, val):
        setattr(self, '_' + var, val)
        self.redraw()

    def _getter(self):
        return getattr(self, '_' + var)

    return property(_getter, _setter)


# A button that can be defined with an arbitrary on-click function.
# Saves the user from creating a new inherited class for every different usage.
# Example:
# self.buttons['end turn'] = button.Button(self, 'self.owner.end_turn()', pos=(60, 40), size=(100, 30), visible=True, text='End Turn')
# Calls the "end_turn()" function of the class that created the button.
class Button(object):
    def __init__(self, owner, function, pos=(50, 50), size=(100, 100), visible=True, enabled=True, colour=(0, 0, 0),
                 border_colour=(0, 0, 0), border_width=2, text=None, **kwargs):
        self._pos = (0, 0)
        self.pos_setter(pos)

        # Other properties' validity are checked in redraw(), this is called whenever they are changed, so exceptions will lead back to the incorrect assignment
        self._size = size  # underscore is "hidden" variable, not for direct access
        self._colour = colour
        self._visible = visible
        self._border_colour = border_colour
        self._border_width = border_width
        self._text = text
        self.enabled = enabled  # whether button can be activated, visible or not

        for arg in kwargs:  # allows for additional arbitrary arguments to be passed in, useful for more complicated button functions
            setattr(self, arg, kwargs[arg])

        self.owner = owner  # container that created the button, allows for the button function to interact with its creator
        self.function = function

        self.surface = pygame.Surface(
            self._size)  # keep track of the button surface, takes more memory but is faster than redrawing every time
        self.redraw()

    def pos_setter(self, pos):
        if pos[0] >= 0 and pos[1] >= 0:
            self._pos = pos
        else:
            raise Exception('Negative button position')

    def pos_getter(self):
        return self._pos

    pos = property(pos_getter, pos_setter)
    # all below variables affect the button surface, so make them properties to redraw on change
    visible = create_property('visible')
    size = create_property('size')
    colour = create_property('colour')
    border_colour = create_property('border_colour')
    border_width = create_property('border_width')
    text = create_property('text')

    def redraw(self):
        if not (self.size[0] > 0 and self.size[1] > 0): raise Exception('Negative button size')
        if not valid_colour(self.border_colour): raise Exception('Invalid button border colour')
        if not valid_colour(self.colour): raise Exception('Invalid button colour')
        if self.border_width < 0: raise Exception('Negative button border width')

        self.surface = pygame.Surface(self.size)

        if not self.visible:
            self.surface.fill((1, 1, 1))
            self.surface.set_colorkey((1, 1, 1))
            return

        # to create border: fill with border colour, then blit a smaller rectangle with main colour
        self.surface.fill(self.border_colour)
        temp = pygame.Surface((self.size[0] - 2 * self.border_width, self.size[1] - 2 * self.border_width))
        temp.fill(self.colour)
        self.surface.blit(temp, (self.border_width, self.border_width))

        font = pygame.font.SysFont('helvetica', 14)
        text = font.render(self.text, True, (200, 200, 200))
        x = self.surface.get_width() / 2 - text.get_width() / 2
        y = self.surface.get_height() / 2 - text.get_height() / 2
        self.surface.blit(text, (x, y))

        self.surface.set_colorkey((1, 1, 1))

    def check_clicked(self, click_pos):  # perform button function if a position is passed in that is within bounds

        pos = self.pos
        w, h = self.size
        w /= 2
        h /= 2

        if abs(click_pos[0] - (pos[0] + w)) < w and abs(click_pos[1] - (pos[1] + h)) < h:
            if self.enabled:
                self.perf_function()

    def perf_function(self):
        self.function()
