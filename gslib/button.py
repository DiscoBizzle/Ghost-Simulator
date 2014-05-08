from __future__ import division, print_function

import pyglet

from gslib.utils import ExecOnChange, exec_on_change_meta
from gslib.constants import *


def valid_color(color):
    if len(color) != 3:
        return False

    for i in color:
        if i < 0 or i > 255:
            return False
    return True


class Button(object):
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
    text_states_toggle = ExecOnChange

    def __init__(self, owner, function=None, pos=(50, 50), order=(0, 0), size=(100, 100), visible=True, enabled=True,
                 color=(0, 0, 0), border_color=(0, 0, 0), border_width=2, text=u'', font_size=10, text_states=None,
                 sprite_batch=None, sprite_group=None, text_batch=None, text_group=None):
        self._pos = pos
        self._size = size
        self._color = color
        self._visible = visible
        self._border_color = border_color
        self._border_width = border_width
        self.text = text
        self.font_size = font_size
        self.text_states = text_states
        self.text_states_toggle = False
        self.enabled = enabled  # whether button can be activated, visible or not
        self._sprite_batch = sprite_batch
        self._sprite_group = sprite_group
        self._text_batch = text_batch
        self._text_group = text_group
        self._visible = visible
        self.owner = owner  # container that created the button, allows for the button function to interact with its creator
        self.function = function
        self.order = order

        self._text_layout = None
        if self._sprite_batch is None:
            self._vertex_list = pyglet.graphics.vertex_list(8, 'v2i', 'c3B')
        else:
            self._vertex_list = self._sprite_batch.add(8, pyglet.gl.GL_QUADS, self._sprite_group, 'v2i', 'c3B')
        if self.visible:
            self._redraw()

        self.priority = False

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        if pos[0] >= 0 and pos[1] >= 0:
            self._pos = pos
            self._update_position()
        else:
            pass
            # raise Exception('Negative button position')

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, border_width):
        if self.border_width < 0:
            raise ValueError('Negative button border width')
        self._border_width = border_width
        self._update_position()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        if not (self.size[0] > 0 and self.size[1] > 0):
            raise ValueError('Negative button size')
        self._size = size
        self._update_text()
        self._update_position()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visible):
        self._visible = visible
        if not visible:
            self._vertex_list.vertices[:] = [0] * 16
            if self._text_layout is not None:
                # delete to remove from batch
                self._text_layout.delete()
                self._text_layout = None
        else:
            self._redraw()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if not valid_color(self.color):
            raise ValueError('Invalid button color')
        self._color = color
        self._update_colors()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, border_color):
        if not valid_color(border_color):
            raise ValueError('Invalid button border color')
        self._border_color = border_color
        self._update_colors()

    def _redraw(self):
        self._update_text()
        self._update_position()
        self._update_colors()

    def _update_text(self):
        if not self.visible:
            return
        if self.text_states:
            self._text = self.text_states[self.text_states_toggle]
        if self._text_layout is None:
            self._text_layout = pyglet.text.Label(text=self._text, font_name=FONT, font_size=self._font_size,
                                                  color=(200, 200, 200, 255), x=self._pos[0], y=self._pos[1],
                                                  width=self._size[0], height=self._size[1], anchor_x='left',
                                                  anchor_y='bottom', align='center', multiline=True,
                                                  batch=self._text_batch, group=self._text_group)
            self._text_layout.content_valign = 'center'
        else:
            self._text_layout.begin_update()
            self._text_layout.text = self._text
            self._text_layout.set_style('font_size', self._font_size)
            self._text_layout.width, self._text_layout.height = self._size
            self._text_layout.end_update()

    def _update_colors(self):
        if not self.visible:
            return
        colors = (self._border_color * 4 + self._color * 4)
        colors = list(colors)
        colors[9:12] = [min(int(x * 1.5), 255) for x in colors[9:12]]
        colors[21:24] = [min(int(x * 1.5), 255) for x in colors[21:24]]
        self._vertex_list.colors[:] = colors

    def _update_position(self):
        if not self.visible:
            return
        # TODO: make faster by only changing the verticies that need it
        self._text_layout.x, self._text_layout.y = self.pos
        outer_rect = [
            self.pos[0], self.pos[1],
            self.pos[0] + self.size[0], self.pos[1],
            self.pos[0] + self.size[0], self.pos[1] + self.size[1],
            self.pos[0], self.pos[1] + self.size[1]]
        inner_rect = [
            self.pos[0] + self.border_width, self.pos[1] + self.border_width,
            self.pos[0] + self.size[0] - self.border_width, self.pos[1] + self.border_width,
            self.pos[0] + self.size[0] - self.border_width, self.pos[1] + self.size[1] - self.border_width,
            self.pos[0] + self.border_width, self.pos[1] + self.size[1] - self.border_width]

        self._vertex_list.vertices[:] = map(int, outer_rect + inner_rect)

    def check_clicked(self, click_pos):  # perform button function if a position is passed in that is within bounds
        if self.check_clicked_no_function(click_pos):
            self.perf_function()
            return True
        return False

    def check_clicked_no_function(self, click_pos):
        x, y = self.pos
        w, h = self.size

        if x <= click_pos[0] < x + w and y <= click_pos[1] < y + h:
            if self.enabled:
                return True
        return False

    def perf_function(self):
        if self.function is not None:
            self.function()

    def text_toggle(self):
        self.text_states_toggle = not self.text_states_toggle

    def draw(self):
        if not self.visible:
            return
        self._vertex_list.draw(pyglet.gl.GL_QUADS)
        self._text_layout.draw()


class DefaultButton(Button):
    def __init__(self, owner, function, pos, text="", size=(100, 20), **kwargs):
        super(DefaultButton, self).__init__(owner, function, size=size, pos=pos, border_color=(120, 50, 80),
                                            border_width=3, color=(120, 0, 0), text=text, **kwargs)
