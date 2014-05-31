from __future__ import absolute_import, division, print_function

from gslib.ui import button, slider
from gslib.utils import ExecOnChange, exec_on_change_meta


def list_func(owner, val, text=None):
    def func():
        if val is None:
            owner.selected_name = "<None>"
            owner.selected = None
        else:
            if text is None:
                owner.selected_name = str(val)
            else:
                owner.selected_name = text
            if isinstance(owner.items, list):
                owner.selected = val
            else:
                owner.selected = owner.items[val]
        if owner.function:
            owner.function()
    return func


class DropDownList(object):

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

    def __init__(self, owner, items, function=None, pos=(50, 50), size=(1, 1), visible=True, enabled=True, color=(120, 0, 0),
                 border_color=(120, 50, 80), border_width=2, text=None, font_size=10, labels='dictkey', order=(0, 0), **kwargs):
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
        self.open = False

        self.function = function

        self.order = order
        self.owner = owner  # container that created the button, allows for the button function to interact with its creator

        self.items = items
        self.selected_name = "<None>"
        self.selected = None
        self.main_button = button.Button(self, None, pos=pos, size=size, font_size=font_size, visible=visible,
                                         text=u"<None>",
                                         border_color=self.border_color, border_width=self.border_width,
                                         color=self.color)
        self.drop_buttons = []

        self.first_time = True
        self.refresh()


        self.high_color = (0, 120, 0)
        self.high_border_color = (0, 200, 0)

        self.update_buttons()
        # self.redraw()

    def refresh(self, new_items=None):  # call if the list changes
        if not new_items is None:
            self.items = new_items

        self.drop_buttons = [button.Button(self, list_func(self, None), size=self.size, font_size=self.font_size,
                                               visible=False, enabled=False, text=u"<None>",
                                               border_color=self.border_color, border_width=self.border_width,
                                               color=self.color)]

        if isinstance(self.items, list):
            for i in self.items:
                if self.labels == 'func_name':
                    t = i.func_name
                else:
                    t = str(i)
                self.drop_buttons.append(button.Button(self, list_func(self, i, t), size=self.size, font_size=self.font_size,
                                                   visible=False, enabled=False, text=t,
                                                   border_color=self.border_color, border_width=self.border_width,
                                                   color=self.color))
        else:
            for k, v in self.items.iteritems():
                if self.labels == 'classname':
                    t = v.__class__.__name__
                    t += ': '
                    t += unicode(k)
                else:
                    t = unicode(k)
                self.drop_buttons.append(button.Button(self, list_func(self, k, t), size=self.size, font_size=self.font_size,
                                                       visible=False, enabled=False, text=t,
                                                       border_color=self.border_color, border_width=self.border_width,
                                                       color=self.color))

        if not self.first_time: # prevent self.function() being run before the owner of this list is fully initialised
            self.set_to_default()
        else:
            self.first_time = False

        if self.open:
            self.update_buttons()

    def update_buttons(self):
        self.main_button.text = self.selected_name
        self.main_button.color = self.color
        self.main_button.border_color = self.border_color
        self.main_button.size = self.size
        self.main_button.visible = self.visible
        self.main_button.font_size = self.font_size
        self.main_button.pos = self.pos
        for i, b in enumerate(self.drop_buttons):
            b.color = self.color
            b.border_color = self.border_color
            b.size = self.size
            b.visible = self.visible
            b.font_size = self.font_size
            b.pos = (self.pos[0], self.pos[1] - (1 + i) * self.size[1])

    def handle_event(self, pos, typ, button=None):
        if not self.enabled:
            return False
        if typ == 'down':
            return self.check_clicked(pos)
        elif typ == 'move' and self.open:
            self.handle_mouse_motion(pos)

    def check_click_within_area(self, click_pos):
        pos = self.pos
        if self.open:
            h = self.size[1] * len(self.drop_buttons)
        else:
            h = 0
        if pos[0] < click_pos[0] < pos[0] + self.size[0] and pos[1] - h < click_pos[1] < pos[1] + self.size[1]:
            return True
        return False

    def check_clicked(self, click_pos, typ='down'):  # show/hide list on click
        pos = self.pos
        w, h = self.size
        w //= 2
        h //= 2

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

        c = False
        for b in self.drop_buttons:
            if b.check_clicked(click_pos):
                c = True
        return c

    def handle_mouse_motion(self, event_pos):
        pos = self.pos
        w, h = self.size
        w //= 2

        eh = pos[1] + h - event_pos[1]
        h_ind = eh // h

        n_drop_button = len(self.drop_buttons)
        if hasattr(self, 'slider'):
            n_drop_button = self.max_display + 1

        # if move off edge, close list
        # if move off bottom or top, close list
        if abs(event_pos[0] - (pos[0] + w)) > w or h_ind > n_drop_button or h_ind < 0:
            self.open = not self.open
            for b in self.drop_buttons:
                b.visible = not b.visible
                b.enabled = not b.enabled
            return

        # highlight the moused-over button

        high_b = None
        for b in self.drop_buttons:
            if b.color != self.color:
                b.color = self.color
            if b.border_color != self.border_color:
                b.border_color = self.border_color

            if b.check_clicked_no_function(event_pos):
                high_b = b

        if high_b:
            if high_b.border_color != self.high_border_color:
                high_b.border_color = self.high_border_color
            if high_b.color != self.high_color:
                high_b.color = self.high_color

    def set_to_default(self):
        self.set_to_value(None)

    def set_to_value(self, value):
        list_func(self, value)()


class DropDownListSlider(DropDownList):
    def __init__(self, owner, items, function=None, max_display=6, *args,  **kwargs):
        self.max_display = max_display - 1
        self.slider = slider.Slider(self, None, horizontal=False)

        super(DropDownListSlider, self).__init__(owner, items, function, *args, **kwargs)

    def refresh(self, new_items=None):
        n_display = min(self.max_display, len(self.drop_buttons))
        n_display += 1
        height = n_display * self.size[1]

        pos = self.pos[0] + self.size[0] - self.slider.size[0], self.pos[1] - height
        self.slider = slider.Slider(self, self.set_scroll, pos=pos, size=(20, height), horizontal=False)
        self.slider.value = 0
        self.set_scroll(0)

        super(DropDownListSlider, self).refresh(new_items)

    def update_buttons(self):
        super(DropDownListSlider, self).update_buttons()
        self.slider.visible = self.open and len(self.drop_buttons) > self.max_display
        self.slider.enabled = self.open and len(self.drop_buttons) > self.max_display
        self.set_scroll(self.slider.value)

        if len(self.drop_buttons) > self.max_display:
            for b in self.drop_buttons:
                b.size = b.size[0] - self.slider.size[0], b.size[1]

    def set_scroll(self, value):
        if not self.open:
            return
        n_scroll = len(self.drop_buttons) - self.max_display
        if n_scroll <= 0:
            return

        slider_range = (self.slider.max - self.slider.min)
        range_per_button = slider_range // n_scroll
        button_n = value // range_per_button # 1 indexed, 0 = show 0th drop button (no scroll)
        if button_n == n_scroll:
            button_n -= 1

        for i, b in enumerate(self.drop_buttons):
            if i < button_n or i > self.max_display + button_n:
                b.visible = False
                b.enabled = False
            else:
                j = i - button_n
                b.pos = self.pos[0], self.pos[1] - (j + 1) * self.size[1]
                b.visible = True
                b.enabled = True

    def check_click_within_area(self, click_pos):
        list_bool = super(DropDownListSlider, self).check_click_within_area(click_pos)
        slider_bool = self.slider.pos[0] < click_pos[0] < self.slider.pos[0] + self.slider.size[0] and \
                    self.slider.pos[1] < click_pos[1] < self.slider.pos[1] + self.slider.size[1]
        return list_bool or slider_bool

    def handle_event(self, pos, typ, butt=None):
        slider_bool = self.slider.check_clicked(pos, typ)
        list_bool = super(DropDownListSlider, self).handle_event(pos, typ, butt)
        return list_bool or slider_bool
