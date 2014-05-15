from __future__ import absolute_import, division, print_function

from gslib import button
from gslib.utils import ExecOnChange, exec_on_change_meta


def list_func(owner, val):
    def func():
        if val is None:
            owner.selected_name = "<None>"
            owner.selected = None
        else:
            owner.selected_name = str(val)
            owner.selected = owner.items[val]
        if owner.function:
            owner.function()
    return func


class List(object):

    __metaclass__ = exec_on_change_meta(["update_buttons"])

    visible = ExecOnChange
    size = ExecOnChange
    color = ExecOnChange
    border_color = ExecOnChange
    border_width = ExecOnChange
    text = ExecOnChange
    font_size = ExecOnChange
    selected_name = ExecOnChange
    pos = ExecOnChange

    def __init__(self, owner, items, function=None, pos=(50, 50), size=(100, 20), visible=True, enabled=True, color=(120, 0, 0),
                 border_color=(120, 50, 80), border_width=2, text=None, font_size=10, labels='dictkey'):
        self.pos = pos
        self.size = size
        self.color = color
        self.visible = visible
        self.border_color = border_color
        self.border_width = border_width
        self.text = text
        self.font_size = font_size
        self.enabled = enabled  # whether button can be activated, visible or not
        self.labels = labels
        #self.priority = False

        self.owner = owner  # container that created the button, allows for the button function to interact with its creator

        self.items = items
        self._selected_name = "<None>"
        self.selected = None
        self.drop_buttons = []
        self.refresh()

        self.open = True
        self.function = function

        self.high_color = (0, 120, 0)
        self.high_border_color = (0, 200, 0)

        self.update_buttons()
        # self.redraw()

    @property
    def open(self):
        return self._open

    @open.setter
    def open(self, n):
        self._open = n
        #self.priority = n
        #for b in self.drop_buttons:
        #    b.priority = n

    def refresh(self):  # call if the list changes
        self.drop_buttons = []

        for k, v in self.items.iteritems():
            if self.labels == 'classname':
                t = v.__class__.__name__
                t += ': '
                t += unicode(k)
            else:
                t = unicode(k)
            self.drop_buttons.append(button.Button(self, list_func(self, k), size=self.size, font_size=self.font_size,
                                                   visible=self.visible, enabled=self.enabled, text=t,
                                                   border_color=self._border_color, border_width=self.border_width,
                                                   color=self.color))
        self.update_buttons()

    def update_buttons(self):
        for i, b in enumerate(self.drop_buttons):
            b.color = self.color
            b.border_color = self.border_color
            b.size = self.size
            b.visible = self.visible
            b.font_size = self.font_size
            b.pos = (self.pos[0], self.pos[1] - (i + 1) * self.size[1])

    def handle_event(self, pos, typ, button=None):
        if not self.enabled:
            return False
        if typ == 'down':
            return self.check_clicked(pos)
        elif typ == 'move':
            self.handle_mouse_motion(pos)

    def check_click_within_area(self, click_pos):
        pos = self.pos
        h = self.size[1] * len(self.drop_buttons)
        if pos[0] < click_pos[0] < pos[0] + self.size[0] and pos[1] - h < click_pos[1] < pos[1]:
            return True
        return False

    def check_clicked(self, click_pos):  # show/hide list on click
        pos = self.pos
        w, h = self.size
        w //= 2
        h //= 2

        if abs(click_pos[0] - (pos[0] + w)) < w and abs(click_pos[1] - (pos[1] + h)) < h:
            self.update_buttons()
            return True

        b = False
        for b in self.drop_buttons:
            if b.check_clicked(click_pos):
                b = True
        return b

    def handle_mouse_motion(self, event_pos):
        pos = self.pos
        w, h = self.size
        w //= 2

        eh = pos[1] + h - event_pos[1]
        h_ind = eh // h

        # highlight the moused-over button
        for b in self.drop_buttons:
            if b.color != self.color:
                b.color = self.color
            if b.border_color != self.border_color:
                b.border_color = self.border_color
        if len(self.drop_buttons) >= h_ind > 0:
            b = self.drop_buttons[h_ind - 1]
            if b.border_color != self.high_border_color:
                b.border_color = self.high_border_color
            if b.color != self.high_color:
                b.color = self.high_color
