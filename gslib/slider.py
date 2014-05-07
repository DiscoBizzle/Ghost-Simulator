from __future__ import division, print_function

import pyglet


def create_property(var):  # creates a member variable that redraws the button when changed.
    def _setter(self, val):
        old_val = getattr(self, '_' + var)
        if old_val != val:
            setattr(self, '_' + var, val)
            self._redraw()

    def _getter(self):
        return getattr(self, '_' + var)

    return property(_getter, _setter)


class Slider(object):
    """
    Basic example:
        s = Slider(self, self.function)
    self.function:
    if slider.enabled == True:
        Function passed in will be called with 1 argument (current value of slider).
        Create function in class that creates the slider and pass it in as second argument.
    """

    def __init__(self, owner, func, pos=(0, 0), range=(0, 100), value=50, size=(100, 20), back_colour=(120, 0, 0),
                 fore_colour=(0, 120, 0), order=(0, 0), enabled=True, visible=True, sprite_batch=None, sprite_group=None):

        self.owner = owner
        self.min, self.max = range
        self._value = value
        self._fore_colour = fore_colour
        self._back_colour = back_colour
        self._size = size
        self._visible = visible
        self.enabled = enabled
        self._pos = pos
        self._sprite_batch = sprite_batch
        self._sprite_group = sprite_group
        if self._sprite_batch is None:
            self._vertex_list = pyglet.graphics.vertex_list(8, 'v2i', 'c3B')
        else:
            self._vertex_list = self._sprite_batch.add(8, pyglet.gl.GL_QUADS, self._sprite_group, 'v2i', 'c3B')

        self.order = order

        self.is_clicked = False

        self.func = func

        self._redraw()

    def get_value(self):
        return self._value
    def set_value(self, val):
        self._value = val
        if self._value > self.max:
            self._value = self.max
        if self._value < self.min:
            self._value = self.min
        self._redraw()
    value = property(get_value, set_value)

    fore_colour = create_property('fore_colour')
    back_colour = create_property('back_colour')
    size = create_property('size')
    pos = create_property('pos')

    def _set_visible(self, visible):
        if visible == self._visible:
            return
        self._visible = visible
        if not visible:
            self._vertex_list.vertices[:] = [0] * 16
        else:
            self._redraw()
    visible = property(lambda self: self._visible, _set_visible)

    def _redraw(self):
        if not self._visible:
            return
        colors = (self.back_colour * 4 + self.fore_colour * 4)
        colors = list(colors)
        colors[9:12] = [min(int(x * 1.5), 255) for x in colors[9:12]]
        colors[21:24] = [min(int(x * 1.5), 255) for x in colors[21:24]]
        self._vertex_list.colors[:] = colors

        length = self.size[0] * ((self.value - self.min) / (self.max - self.min))

        back_rect = [
            self.pos[0], self.pos[1],
            self.pos[0] + self.size[0], self.pos[1],
            self.pos[0] + self.size[0], self.pos[1] + self.size[1],
            self.pos[0], self.pos[1] + self.size[1]]
        fore_rect = [
            self.pos[0], self.pos[1],
            self.pos[0] + length, self.pos[1],
            self.pos[0] + length, self.pos[1] + self.size[1],
            self.pos[0], self.pos[1] + self.size[1]]

        self._vertex_list.vertices[:] = map(int, back_rect + fore_rect)

    def check_clicked(self, pos, typ):
        if not self.enabled:
            return
        click_pos = pos
        w, h = self.size
        w /= 2
        h /= 2

        if typ == 'up':
            self.is_clicked = False
            return

        if typ == 'down' and abs(click_pos[0] - (self.pos[0] + w)) < w and abs(click_pos[1] - (self.pos[1] + h)) < h:
            self.is_clicked = True

        if self.is_clicked:
            frac = (click_pos[0] - self.pos[0]) / self.size[0]
            self.value = self.min + (self.max - self.min) * frac
            self.func(self.value)

    def draw(self):
        self._vertex_list.draw(pyglet.gl.GL_QUADS)
