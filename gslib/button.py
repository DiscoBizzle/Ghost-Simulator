from __future__ import division, print_function

import pyglet

from gslib.constants import *


def valid_colour(colour):
    if len(colour) != 3:
        return False

    for i in colour:
        if i < 0 or i > 255:
            return False
    return True


def create_text_property(var):  # creates a member variable that redraws the text when changed.
    def _setter(self, val):
        old_val = getattr(self, '_' + var)
        if val != old_val:
            setattr(self, '_' + var, val)
            self._update_text()

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

    def __init__(self, owner, function=None, pos=(50, 50), order=(0, 0), size=(100, 100), visible=True, enabled=True,
                 colour=(0, 0, 0), border_colour=(0, 0, 0), border_width=2, text=u'', font_size=10, text_states=None,
                 sprite_batch=None, sprite_group=None, text_batch=None, text_group=None):
        self._pos = pos
        self._size = size
        self._color = colour
        self._visible = visible
        self._border_color = border_colour
        self._border_width = border_width
        self._text = text
        self._font_size = font_size
        self.text_states = text_states
        self._text_states_toggle = False
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
        self._redraw()

        self.priority = False

    def _set_pos(self, pos):
        if pos == self._pos:
            return
        if pos[0] >= 0 and pos[1] >= 0:
            self._pos = pos
            self._update_position()
        else:
            pass
            # raise Exception('Negative button position')
    pos = property(lambda self: self._pos, _set_pos)

    text = create_text_property('text')
    font_size = create_text_property('font_size')
    text_states_toggle = create_text_property('text_states_toggle')

    def _set_border_width(self, border_width):
        if border_width == self._border_width:
            return
        if self.border_width < 0:
            raise Exception('Negative button border width')
        self._border_width = border_width
        self._update_position()
    border_width = property(lambda self: self._border_width, _set_border_width)

    def _set_size(self, size):
        if size == self._size:
            return
        if not (self.size[0] > 0 and self.size[1] > 0):
            raise Exception('Negative button size')
        self._size = size
        self._update_text()
        self._update_position()
    size = property(lambda self: self._size, _set_size)

    def _set_visible(self, visible):
        if visible == self._visible:
            return
        self._visible = visible
        if not visible:
            self._vertex_list.vertices[:] = [0] * 16
            if self._text_layout is not None:
                # delete to remove from batch
                self._text_layout.delete()
                self._text_layout = None
        else:
            self._redraw()
    visible = property(lambda self: self._visible, _set_visible)

    def _set_color(self, color):
        if color == self._color:
            return
        if not valid_colour(self.colour):
            raise Exception('Invalid button colour')
        self._color = color
        self._update_colors()
    colour = property(lambda self: self._color, _set_color)

    def _set_border_colour(self, border_colour):
        if border_colour == self._border_color:
            return
        if not valid_colour(self.border_colour):
            raise Exception('Invalid button border colour')
        self._border_color = border_colour
        self._update_colors()
    border_colour = property(lambda self: self._border_color, _set_border_colour)

    def _redraw(self):
        self._update_text()
        self._update_position()
        self._update_colors()

    def _update_text(self):
        if not self._visible:
            return
        if self.text_states:
            self._text = self.text_states[self.text_states_toggle]
        if self._text_layout is not None:
            # delete to remove from batch
            self._text_layout.delete()
        self._text_layout = pyglet.text.Label(text=self._text, font_name=FONT, font_size=self._font_size,
                                              color=(200, 200, 200, 255), x=self._pos[0], y=self._pos[1],
                                              width=self._size[0], height=self._size[1], anchor_x='left',
                                              anchor_y='bottom', align='center', multiline=True, batch=self._text_batch,
                                              group=self._text_group)
        self._text_layout.content_valign = 'center'

    def _update_colors(self):
        if not self._visible:
            return
        colors = (self._border_color * 4 + self._color * 4)
        self._vertex_list.colors[:] = colors

    def _update_position(self):
        if not self._visible:
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
        x, y = self._pos
        w, h = self._size

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
        if not self._visible:
            return
        self._vertex_list.draw(pyglet.gl.GL_QUADS)
        self._text_layout.draw()


class DefaultButton(Button):
    def __init__(self, owner, function, pos, text="", size=(100, 20), **kwargs):
        super(DefaultButton, self).__init__(owner, function, size=size, pos=pos, border_colour=(120, 50, 80),
                                            border_width=3, colour=(120, 0, 0), text=text, **kwargs)
