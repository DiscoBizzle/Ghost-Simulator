from __future__ import absolute_import, division, print_function

import pyglet
from pyglet import gl
from pyglet.window import mouse

from gslib.engine import primitives
from gslib.utils import ExecOnChange, exec_on_change_meta
from gslib.constants import *
from gslib import window

from gslib.ui.control import Control


def valid_color(color):
    if len(color) != 3:
        return False

    for i in color:
        if i < 0 or i > 255:
            return False
    return True


class Button(Control, pyglet.event.EventDispatcher):
    """
    Basic example:
        b = Button(self, self.function)
    self.function:
    if button.enabled == True:
        Function passed in will be called with 0 arguments.
        Create function in class that creates the button and pass it in as second argument.
    """

    __metaclass__ = exec_on_change_meta(["_update_text"])

    text = ExecOnChange
    font_size = ExecOnChange
    text_font = ExecOnChange
    text_color = ExecOnChange

    def __init__(self, owner=None, function=None, color=(128, 128, 128), border_color=(180, 180, 180), border_width=2,
                 text=u'', font_size=10, text_font=None, text_color=(200, 200, 200, 255), window=window, **kwargs):
        super(Button, self).__init__(window=window, **kwargs)
        self._color = color
        self._border_color = border_color
        self._border_width = border_width
        self.text = text
        self.font_size = font_size
        self.text_font = text_font
        self.text_color = text_color
        self._sprite_group = primitives.PrimitiveGroup(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA,
                                                       self._backgroud_group)
        self.owner = owner
        if function is not None:
            self.on_click_up = function
        self._pressed = False

        self._text_layout = None
        self._vertex_list = self._create_vertex_list()

        self._main_window_handlers = {'on_mouse_press': self.on_mouse_press}
        self._extra_window_handlers = {'on_mouse_release': self.on_mouse_release,
                                       'on_mouse_leave': self.on_mouse_leave,
                                       'on_mouse_drag': self.on_mouse_drag}

        self._update()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, value):
        assert value >= 0, 'Negative button border width'
        self._border_width = value
        self._update_position()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        if not value:
            self._vertex_list.vertices[:] = [0] * 16
            if self._text_layout is not None and self._batch is not None:
                # delete to remove from batch
                self._text_layout.delete()
                self._text_layout = None
        else:
            self._update()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        assert valid_color(value), 'Invalid button color'
        self._color = value
        self._update_colors()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, value):
        assert valid_color(value), 'Invalid button border color'
        self._border_color = value
        self._update_colors()

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        self._pressed = value
        self._update_colors()

    def _update(self):
        self._update_text()
        self._update_position()
        self._update_size()
        self._update_colors()

    def _update_text(self):
        if not self.visible:
            return
        if self._text_layout is None:
            self._text_layout = self._create_text_leyout()
        else:
            self._text_layout.begin_update()
            self._text_layout.text = self.text
            self._text_layout.font_size = self.font_size
            self._text_layout.font_name = self.text_font
            self._text_layout.color = self.text_color
            self._text_layout.end_update()

    def _create_vertex_list(self):
        if self._batch is None:
            return pyglet.graphics.vertex_list(8, 'v2i', 'c3B')
        else:
            return self._batch.add(8, gl.GL_QUADS, self._sprite_group, 'v2i', 'c3B')

    def _create_text_leyout(self):
        text_layout = pyglet.text.Label(text=self.text, font_name=self.text_font, font_size=self.font_size,
                                        color=self.text_color, x=self.x, y=self.y, width=self.width,
                                        height=self.height, anchor_x='left', anchor_y='bottom', align='center',
                                        multiline=True, batch=self._batch, group=self._text_group)
        text_layout.content_valign = 'center'
        return text_layout

    def _update_colors(self):
        if not self.visible:
            return
        colors = list(self._border_color * 4 + self._color * 4)
        if self.pressed:
            colors[3:6] = (min(int(x * 1.5), 255) for x in colors[3:6])
            colors[15:18] = (min(int(x * 1.5), 255) for x in colors[15:18])
        else:
            colors[9:12] = (min(int(x * 1.5), 255) for x in colors[9:12])
            colors[21:24] = (min(int(x * 1.5), 255) for x in colors[21:24])
        self._vertex_list.colors[:] = colors

    def _update_position(self):
        if not self.visible:
            return
        self._text_layout.x, self._text_layout.y = self.pos
        self._update_verticies()

    def _update_size(self):
        if not self.visible:
            return
        self._text_layout.begin_update()
        self._text_layout.width, self._text_layout.height = self.size
        self._text_layout.end_update()
        self._update_verticies()

    def _update_verticies(self):
        outer_rect = [
            self.x, self.y,
            self.x + self.width, self.y,
            self.x + self.width, self.y + self.height,
            self.x, self.y + self.height]

        inner_rect = [
            self.x + self.border_width, self.y + self.border_width,
            self.x + self.width - self.border_width, self.y + self.border_width,
            self.x + self.width - self.border_width, self.y + self.height - self.border_width,
            self.x + self.border_width, self.y + self.height - self.border_width]

        self._vertex_list.vertices[:] = map(int, outer_rect + inner_rect)

    def _update_enabled(self):
        if self.enabled:
            self.create_handlers()
        else:
            self.pressed = False
            self.delete_handlers()

    def draw(self):
        if not self.visible:
            return
        self._sprite_group.set_state_recursive()
        self._vertex_list.draw(gl.GL_QUADS)
        self._sprite_group.unset_state_recursive()
        self._text_layout.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT and self.in_bounds(x, y):
            self.dispatch_event('on_click_down')
            self.pressed = True
            if self._window is not None:
                self._window.push_handlers(**self._extra_window_handlers)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if self.in_bounds(x, y):
                self.dispatch_event('on_click_up')
            self.pressed = False
            if self._window is not None:
                self._window.remove_handlers(**self._extra_window_handlers)

    def on_mouse_leave(self, x, y):
        self.pressed = False
        if self._window is not None:
            self._window.remove_handlers(**self._extra_window_handlers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.pressed = self.in_bounds(x, y)
        self.dispatch_event('on_drag', dx, dy)

    def create_handlers(self):
        if self._window is not None:
            self._window.push_handlers(**self._main_window_handlers)

    def delete_handlers(self):
        if self._window is not None:
            self._window.remove_handlers(**self._main_window_handlers)
            self._window.remove_handlers(**self._extra_window_handlers)

    def __del__(self):
        self.delete()

    def delete(self):
        self.delete_handlers()
        if self._text_layout is not None:
            self._text_layout.delete()
            self._text_layout = None
        if self._vertex_list is not None:
            self._vertex_list.delete()
            self._vertex_list = None

Button.register_event_type('on_click_up')
Button.register_event_type('on_click_down')
Button.register_event_type('on_drag')


class DefaultButton(Button):
    def __init__(self, owner, function, order=(0, 0), size=(100, 20), border_color=(120, 50, 80), border_width=3,
                 color=(120, 0, 0), text_font=FONT, text_color=(200, 200, 200, 255), **kwargs):
        self.order = order
        super(DefaultButton, self).__init__(owner=owner, function=function, size=size, border_color=border_color,
                                            border_width=border_width, color=color, text_font=text_font,
                                            text_color=text_color, **kwargs)

    def flip_color_rg(self, value=None):
        low_color = (120, 0, 0)
        low_border_color = (120, 50, 80)

        high_color = (0, 120, 0)
        high_border_color = (0, 200, 0)

        if not value is None:
            if value:
                self.color = high_color
                self.border_color = high_border_color
            else:
                self.color = low_color
                self.border_color = low_border_color
        else:
            if self.color == low_color:
                self.color = high_color
                self.border_color = high_border_color
            elif self.color == high_color:
                self.color = low_color
                self.border_color = low_border_color


class CheckBox(Button):
    def __init__(self, owner, bool_property, text=u"", size=(100, 20), **kwargs):
        super(CheckBox, self).__init__(owner, function=None, size=size, border_color=(120, 50, 80),
                                       border_width=3, color=(120, 0, 0), text=text, **kwargs)

        self.property_name = bool_property

        self.low_color = (120, 0, 0)
        self.low_border_color = (120, 50, 80)

        self.high_color = (0, 120, 0)
        self.high_border_color = (0, 200, 0)

        self.update()

    def update(self):
        a = getattr(self.owner, self.property_name)
        if a:
            self.color = self.high_color
            self.border_color = self.high_border_color
        else:
            self.color = self.low_color
            self.border_color = self.low_border_color

    def perf_function(self):
        a = getattr(self.owner, self.property_name)
        setattr(self.owner, self.property_name, not a)
        self.update()
