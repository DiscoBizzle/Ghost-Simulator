import pyglet

from gslib.constants import *
from gslib import graphics
from gslib import text

def valid_colour(colour):
    if len(colour) != 3:
        return False
        
    for i in colour:
        if i < 0 or i > 255:
            return False
    return True


def create_property(var):  # creates a member variable that redraws the button when changed.
    def _setter(self, val):
        setattr(self, '_' + var, val)
        self.redraw()

    def _getter(self):
        return getattr(self, '_' + var)

    return property(_getter, _setter)


class Button(object):
    """
    Basic example:
        b = Button(self, self.function)
    self.function:
    if button.enabled == True:
        Function passed in will be called with 0 arguments.
        Create function in class that creates the button and pass it in as second argument.
    """
    def __init__(self, owner, function, pos=(50, 50), size=(100, 100), visible=True, enabled=True, colour=(0, 0, 0),
                 border_colour=(0, 0, 0), border_width=2, text=None, font_size=10, text_states=None, **kwargs):
        self._pos = pos

        # Other properties' validity are checked in redraw(), this is called whenever they are changed, so exceptions will lead back to the incorrect assignment
        self._size = size  # underscore is "hidden" variable, not for direct access
        self._colour = colour
        self._visible = True # ensures button gets drawn, otherwise can't change its position
        self._border_colour = border_colour
        self._border_width = border_width
        self._text = text
        self._text_dirty = None
        self._font_size = font_size
        self.text_states = text_states
        self.text_states_toggle = False
        self.enabled = enabled  # whether button can be activated, visible or not

        for arg in kwargs:  # allows for additional arbitrary arguments to be passed in, useful for more complicated button functions
            setattr(self, arg, kwargs[arg])

        self.owner = owner  # container that created the button, allows for the button function to interact with its creator
        self.function = function

        self.outer_sprite = graphics.new_rect_sprite()
        self.inner_sprite = graphics.new_rect_sprite()
        self.text_sprite = None
        self.sprites = [self.outer_sprite, self.inner_sprite, self.text_sprite]
        self.redraw()
        self._visible = visible

        self.priority = False

    def pos_setter(self, pos):
        if pos[0] >= 0 and pos[1] >= 0:
            self._pos = pos
            self.update_position()
        else:
            pass
            # raise Exception('Negative button position')

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
    font_size = create_property('font_size')

    def redraw(self):
        if not (self.size[0] > 0 and self.size[1] > 0): raise Exception('Negative button size')
        if not valid_colour(self.border_colour): raise Exception('Invalid button border colour')
        if not valid_colour(self.colour): raise Exception('Invalid button colour')
        if self.border_width < 0: raise Exception('Negative button border width')

        if self.text_states:
            self._text = self.text_states[self.text_states_toggle]

        if not self._visible:
            return

        self.outer_sprite.color_rgb = self.border_colour
        self.inner_sprite.color_rgb = self.colour

        self.outer_sprite.scale_x = self.size[0]
        self.outer_sprite.scale_y = self.size[1]
        self.inner_sprite.scale_x = self.size[0] - self._border_width * 2
        self.inner_sprite.scale_y = self.size[1] - self._border_width * 2

        self.outer_sprite.position = self.pos
        self.inner_sprite.position = (self.pos[0] + self._border_width, self.pos[1] + self._border_width)

        # do we need to rerender text? rendering text is SLOW. (< 30 fps)
        text_dirty_new = [self.text, self.font_size, self.size[0], self.size[1]]
        if self._text_dirty is None or self._text_dirty != text_dirty_new:
            self.text_sprite = text.new(text=self.text, font_size=self.font_size, centered=True,
                                         width=self.size[0], height=self.size[1])
            self.text_sprite.color = (200, 200, 200, 255)
            self._text_dirty = text_dirty_new

        self.text_sprite.x = self.pos[0] # + self.outer_sprite.width / 2 - self.text_sprite.width / 2
        self.text_sprite.y = self.pos[1] # + self.outer_sprite.height / 2 - self.text_sprite.height / 2

        self.sprites = [self.outer_sprite, self.inner_sprite, self.text_sprite]

    def update_position(self):
        self.outer_sprite.position = self.pos
        self.inner_sprite.position = (self.pos[0] + self._border_width, self.pos[1] + self._border_width)
        self.text_sprite.x = self.pos[0]
        self.text_sprite.y = self.pos[1]


    def check_clicked(self, click_pos):  # perform button function if a position is passed in that is within bounds
        pos = self.pos
        w, h = self._size
        w /= 2
        h /= 2

        if abs(click_pos[0] - (pos[0] + w)) < w and abs(click_pos[1] - (pos[1] + h)) < h:
            if self.enabled:
                self.perf_function()
                return True
        return False

    def check_clicked_no_function(self, click_pos):
        pos = self.pos
        w, h = self._size
        w /= 2
        h /= 2

        if abs(click_pos[0] - (pos[0] + w)) < w and abs(click_pos[1] - (pos[1] + h)) < h:
            if self.enabled:
                return True
        return False

    def perf_function(self):
        if self.function is not None:
            self.function()

    def text_toggle(self):
        self.text_states_toggle = not self.text_states_toggle


class DefaultButton(Button):
    def __init__(self, owner, function, pos, text="", size=(100, 20), **kwargs):
        Button.__init__(self, owner, function, size=size, pos=pos, border_colour=(120, 50, 80), border_width=3,
                        colour=(120, 0, 0), text=text, **kwargs)
