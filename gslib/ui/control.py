from __future__ import absolute_import, division, print_function

import pyglet


class Control(object):
    def __init__(self, pos=(0, 0), size=(1, 1), visible=True, window=None, batch=None, group=None):
        self._x, self._y = pos
        self._width, self._height = size
        self._visible = visible
        self._enabled = False
        self._window = window
        self._batch = batch
        self._group = group

        self._backgroud_group = pyglet.graphics.OrderedGroup(0, group)
        self._text_group = pyglet.graphics.OrderedGroup(1, group)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            self._enabled = value
            self._update_enabled()

    @property
    def pos(self):
        return self._x, self._y
    
    @pos.setter
    def pos(self, value):
        self._x, self._y = value
        self._update_position()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._update_position()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._update_position()

    @property
    def size(self):
        return self._width, self._height

    @size.setter
    def size(self, value):
        assert value[0] > 0 and value[1] > 0, 'Invalid Control size'
        self._width, self._height = value
        self._update_size()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        assert value > 0, 'Invalid Control width'
        self._width = value
        self._update_size()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        assert value > 0, 'Invalid Control height'
        self._height = value
        self._update_size()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self._update()

    def _update(self):
        self._update_position()
        self._update_size()
        self._update_enabled()

    def _update_position(self):
        raise NotImplementedError()

    def _update_size(self):
        raise NotImplementedError()

    def _update_enabled(self):
        raise NotImplementedError()

    def in_bounds(self, x, y):
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
