import pygame
from gslib import button
from gslib.constants import *


def create_property(var):  # creates a member variable that redraws the button when changed.
    def _setter(self, val):
        setattr(self, '_' + var, val)
        self.update_buttons()
        # self.redraw()

    def _getter(self):
        return getattr(self, '_' + var)

    return property(_getter, _setter)


def list_func(owner, val):
    def func():
        if val is None:
            owner.selected_name = "<None>"
            owner.selected = None
        else:
            owner.selected_name = str(val)
            owner.selected = owner.items[val]
        owner.function()
    return func


class DropDownList(object):
    def __init__(self, owner, items, function=None, pos=(50, 50), size=(100, 20), visible=True, enabled=True, colour=(120, 0, 0),
                 border_colour=(120, 50, 80), border_width=2, text=None, font_size=10, labels='dictkey', **kwargs):
        self._pos = pos

        self._size = size
        self._colour = colour
        self._visible = visible
        self._border_colour = border_colour
        self._border_width = border_width
        self._text = text
        self._font_size = font_size
        self.enabled = enabled  # whether button can be activated, visible or not
        self.labels = labels

        for arg in kwargs:  # allows for additional arbitrary arguments to be passed in, useful for more complicated functions
            setattr(self, arg, kwargs[arg])

        self.owner = owner  # container that created the button, allows for the button function to interact with its creator

        self.items = items
        self._selected_name = "<None>"
        self.selected = None
        self.main_button = button.Button(self, None, pos=pos, size=size, font_size=font_size, visible=visible,
                                         text=u"<None>",
                                         border_colour=self._border_colour, border_width=self.border_width,
                                         colour=self.colour)
        self.drop_buttons = []
        self.refresh()

        self.open = False
        self.function = function

        self.high_colour = (0, 120, 0)
        self.high_border_colour = (0, 200, 0)

        self.surface = pygame.Surface(self._size)
        self.update_buttons()
        # self.redraw()

    # all below variables affect the button surface, so make them properties to redraw on change
    visible = create_property('visible')
    size = create_property('size')
    colour = create_property('colour')
    border_colour = create_property('border_colour')
    border_width = create_property('border_width')
    text = create_property('text')
    font_size = create_property('font_size')
    selected_name = create_property('selected_name')
    pos = create_property('pos')

    def refresh(self):  # call if the list changes
        self.drop_buttons = []
        self.drop_buttons.append(button.Button(self, list_func(self, None), size=self.size, font_size=self.font_size,
                                               visible=False, enabled=False, text=u"<None>",
                                               border_colour=self._border_colour, border_width=self.border_width,
                                               colour=self.colour))

        for k, v in self.items.iteritems():
            if self.labels == 'classname':
                t = v.__class__.__name__
                t += ': '
                t += unicode(k)
            else:
                t = unicode(k)
            self.drop_buttons.append(button.Button(self, list_func(self, k), size=self.size, font_size=self.font_size,
                                                   visible=False, enabled=False, text=t,
                                                   border_colour=self._border_colour, border_width=self.border_width,
                                                   colour=self.colour))

    def update_buttons(self):
        self.main_button.text = self.selected_name
        self.main_button.colour = self.colour
        self.main_button.border_colour = self.border_colour
        self.main_button.size = self.size
        self.main_button.visible = self.visible
        self.main_button.font_size = self.font_size
        self.main_button.pos = self.pos
        for i, b in enumerate(self.drop_buttons):
            b.colour = self.colour
            b.border_colour = self.border_colour
            b.size = self.size
            b.visible = self.visible
            b.font_size = self.font_size
            b.pos = (self.pos[0], self.pos[1] - (1 + i) * self.size[1])

    def handle_event(self, pos, typ, button=None):
        if not self.enabled:
            return
        if typ == 'down':
            return self.check_clicked(pos)
        elif typ == 'move' and self.open:
            self.handle_mouse_motion(pos)

    def check_clicked(self, click_pos):  # show/hide list on click
        pos = self.pos
        w, h = self.size
        w /= 2
        h /= 2

        if abs(click_pos[0] - (pos[0] + w)) < w and abs(click_pos[1] - (pos[1] + h)) < h:
            self.open = not self.open
            for b in self.drop_buttons:
                b.visible = not b.visible
                b.enabled = not b.enabled
            self.update_buttons()
            # self.redraw()
            return True

        if not self.open:
            return

        for b in self.drop_buttons:
            b.check_clicked(click_pos)

    def handle_mouse_motion(self, event_pos):
        pos = self.pos
        w, h = self.size
        w /= 2

        eh = pos[1] + h - event_pos[1]
        h_ind = eh / h

        # if move off edge, close list
        # if move off bottom or top, close list
        if abs(event_pos[0] - (pos[0] + w)) > w or h_ind > len(self.drop_buttons) or h_ind < 0:
            self.open = not self.open
            for b in self.drop_buttons:
                b.visible = not b.visible
                b.enabled = not b.enabled
            return

        # highlight the moused-over button

        for b in self.drop_buttons:
            if b.colour != self.colour:
                b.colour = self.colour
            if b.border_colour != self.border_colour:
                b.border_colour = self.border_colour
        if h_ind > 0:
            b = self.drop_buttons[h_ind - 1]
            if b.border_colour != self.high_border_colour:
                b.border_colour = self.high_border_colour
            if b.colour != self.high_colour:
                b.colour = self.high_colour
