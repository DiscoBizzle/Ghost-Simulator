from __future__ import absolute_import, division, print_function

from gslib.utils import ExecOnChange, exec_on_change_meta

import pyglet
from pyglet.window import mouse


class Slider(object):
    """
    Basic example:
        s = Slider(self, self.function)
    self.function:
    if slider.enabled == True:
        Function passed in will be called with 1 argument (current value of slider).
        Create function in class that creates the slider and pass it in as second argument.
    """

    __metaclass__ = exec_on_change_meta(["redraw"])
    fore_color = ExecOnChange
    back_color = ExecOnChange
    size = ExecOnChange
    pos = ExecOnChange

    def __init__(self, owner=None, function=None, pos=(0, 0), range=(0, 100), value=50, size=(100, 20), back_color=(120, 0, 0),
                 fore_color=(0, 120, 0), enabled=True, visible=True, window=None, batch=None, group=None,
                 horizontal=True):

        self._window = window
        self.owner = owner
        self.min, self.max = range
        self._visible = visible
        self._value = value
        self.fore_color = fore_color
        self.back_color = back_color
        self.size = size
        self.enabled = enabled
        self.pos = pos
        self._batch = batch
        self._group = pyglet.graphics.OrderedGroup(0, group)
        if self._batch is None:
            self.vertex_list = pyglet.graphics.vertex_list(8, 'v2i', 'c3B')
        else:
            self.vertex_list = self._batch.add(8, pyglet.gl.GL_QUADS, self._group, 'v2i', 'c3B')

        self.is_clicked = False

        self.func = function

        self.horizontal = horizontal

        self.redraw()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        if self._value > self.max:
            self._value = self.max
        if self._value < self.min:
            self._value = self.min
        self.redraw()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visible):
        self._visible = visible
        if not visible:
            self.vertex_list.vertices[:] = [0] * 16
        else:
            self.redraw()

    def redraw(self):
        if not self.visible:
            return
        colors = (self.back_color * 4 + self.fore_color * 4)
        colors = list(colors)
        colors[9:12] = [min(int(x * 1.5), 255) for x in colors[9:12]]
        colors[21:24] = [min(int(x * 1.5), 255) for x in colors[21:24]]
        self.vertex_list.colors[:] = colors


        back_rect = [
            self.pos[0], self.pos[1],
            self.pos[0] + self.size[0], self.pos[1],
            self.pos[0] + self.size[0], self.pos[1] + self.size[1],
            self.pos[0], self.pos[1] + self.size[1]]

        if self.horizontal:
            length = self.size[0] * ((self.value - self.min) / (self.max - self.min))
            fore_rect = [
                self.pos[0], self.pos[1],
                self.pos[0] + length, self.pos[1],
                self.pos[0] + length, self.pos[1] + self.size[1],
                self.pos[0], self.pos[1] + self.size[1]]
        else:
            height = self.size[1] * ((self.value - self.min) / (self.max - self.min))
            fore_rect = [
                self.pos[0], self.pos[1] + self.size[1] - height,
                self.pos[0] + self.size[0], self.pos[1] + self.size[1] - height,
                self.pos[0] + self.size[0], self.pos[1] + self.size[1],
                self.pos[0], self.pos[1] + self.size[1]]

        self.vertex_list.vertices[:] = map(int, back_rect + fore_rect)

    def check_clicked(self, pos, typ):
        if not self.enabled:
            return False
        click_pos = pos
        w, h = self.size
        w //= 2
        h //= 2

        if typ == 'up':
            self.is_clicked = False
            return False

        if typ == 'down' and abs(click_pos[0] - (self.pos[0] + w)) < w and abs(click_pos[1] - (self.pos[1] + h)) < h:
            self.is_clicked = True

        if self.is_clicked:
            if self.horizontal:
                frac = (click_pos[0] - self.pos[0]) / self.size[0]
            else:
                frac = (self.pos[1] + self.size[1] - click_pos[1]) / self.size[1] # measured from top
            self.value = self.min + (self.max - self.min) * frac
            self.func(self.value)
            return True
        return False

    def clicked(self, x, y):
        if self.horizontal:
            frac = (x - self.pos[0]) / self.size[0]
        else:
            frac = (self.pos[1] + self.size[1] - y) / self.size[1] # measured from top
        self.value = self.min + (self.max - self.min) * frac
        self.func(self.value)

    def in_bounds(self, x, y):
        control_x, control_y = self.pos
        width, height = self.size

        return (control_x <= x < control_x + width and
                control_y <= y < control_y + height)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            self.clicked(x, y)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT and self.enabled and self.in_bounds(x, y):
            if self._window is not None:
                self._window.push_handlers(on_mouse_drag=self.on_mouse_drag,
                                           on_mouse_release=self.on_mouse_release,
                                           on_mouse_leave=self.on_mouse_leave)
            self.clicked(x, y)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            if self._window is not None:
                self._window.remove_handlers(on_mouse_drag=self.on_mouse_drag,
                                             on_mouse_release=self.on_mouse_release,
                                             on_mouse_leave=self.on_mouse_leave)

    def on_mouse_leave(self, x, y):
        if self._window is not None:
            self._window.remove_handlers(on_mouse_drag=self.on_mouse_drag,
                                         on_mouse_release=self.on_mouse_release,
                                         on_mouse_leave=self.on_mouse_leave)

    def create_handlers(self):
        if self._window is not None:
            self._window.push_handlers(on_mouse_press=self.on_mouse_press)

    def delete_handlers(self):
        if self._window is not None:
            self._window.remove_handlers(on_mouse_press=self.on_mouse_press)

    def update(self):
        self.redraw()

    def draw(self):
        self.vertex_list.draw(pyglet.gl.GL_QUADS)
