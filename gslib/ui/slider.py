from __future__ import absolute_import, division, print_function

from gslib.utils import ExecOnChange, exec_on_change_meta

import pyglet
from pyglet.window import mouse
from pyglet import gl

from gslib.engine import primitives
from gslib.ui import control
from gslib import window


class Slider(control.Control, pyglet.event.EventDispatcher):
    """
    Basic example:
        s = Slider(self, self.function)
    self.function:
    if slider.enabled == True:
        Function passed in will be called with 1 argument (current value of slider).
        Create function in class that creates the slider and pass it in as second argument.
    """

    __metaclass__ = exec_on_change_meta(["update"])
    fore_color = ExecOnChange
    back_color = ExecOnChange

    def __init__(self, owner=None, function=None, range=(0, 100), value=50, back_color=(120, 0, 0),
                 fore_color=(0, 120, 0), horizontal=True, window=window, **kwargs):
        super(Slider, self).__init__(window=window, **kwargs)

        self.owner = owner
        self.min, self.max = range
        self._value = value
        self.fore_color = fore_color
        self.back_color = back_color
        self._group = primitives.PrimitiveGroup(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA, self._backgroud_group)
        if self._batch is None:
            self.vertex_list = pyglet.graphics.vertex_list(8, 'v2i', 'c3B')
        else:
            self.vertex_list = self._batch.add(8, gl.GL_QUADS, self._group, 'v2i', 'c3B')

        self.is_clicked = False

        if function is not None:
            self.on_value_change = function

        self.horizontal = horizontal

        self._update()

    def _update_size(self):
        self.redraw()

    def _update_position(self):
        self.redraw()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value > self.max:
            self._value = self.max
        elif value < self.min:
            self._value = self.min
        else:
            self._value = value
        self._update()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        if not value:
            self.vertex_list.vertices[:] = [0] * 16
        else:
            self._update()

    def redraw(self):
        if not self.visible:
            return
        colors = list(self.back_color * 4 + self.fore_color * 4)
        colors[9:12] = (min(int(x * 1.5), 255) for x in colors[9:12])
        colors[21:24] = (min(int(x * 1.5), 255) for x in colors[21:24])
        self.vertex_list.colors[:] = colors

        back_rect = [
            self.x, self.y,
            self.x + self.width, self.y,
            self.x + self.width, self.y + self.height,
            self.x, self.y + self.height]

        if self.horizontal:
            length = self.width * ((self.value - self.min) / (self.max - self.min))
            fore_rect = [
                self.x, self.y,
                self.x + length, self.y,
                self.x + length, self.y + self.height,
                self.x, self.y + self.height]
        else:
            height = self.height * ((self.value - self.min) / (self.max - self.min))
            fore_rect = [
                self.x, self.y + self.height - height,
                self.x + self.width, self.y + self.height - height,
                self.x + self.width, self.y + self.height,
                self.x, self.y + self.height]

        self.vertex_list.vertices[:] = map(int, back_rect + fore_rect)

    def _update_enabled(self):
        if self.enabled:
            self.create_handlers()
        else:
            self.delete_handlers()

    def clicked(self, x, y):
        old_value = self.value
        if self.horizontal:
            frac = (x - self.x) / self.width
        else:
            frac = (self.y + self.height - y) / self.height  # measured from top
        self.value = self.min + (self.max - self.min) * frac
        if self.value != old_value:
            self.dispatch_event('on_value_change', self.value)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.clicked(x, y)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT and self.enabled and self.in_bounds(x, y):
            if self._window is not None:
                self._window.push_handlers(on_mouse_drag=self.on_mouse_drag,
                                           on_mouse_release=self.on_mouse_release,
                                           on_mouse_leave=self.on_mouse_leave)
            self.clicked(x, y)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
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

    def _update(self):
        self.redraw()

    def draw(self):
        self._group.set_state_recursive()
        self.vertex_list.draw(gl.GL_QUADS)
        self._group.unset_state_recursive()

    def __del__(self):
        self.delete()

    def delete(self):
        if self._window is not None:
            self._window.remove_handlers(on_mouse_press=self.on_mouse_press)
            self._window.remove_handlers(on_mouse_drag=self.on_mouse_drag,
                                         on_mouse_release=self.on_mouse_release,
                                         on_mouse_leave=self.on_mouse_leave)
        if self.vertex_list is not None:
            self.vertex_list.delete()
            self.vertex_list = None

Slider.register_event_type('on_value_change')
