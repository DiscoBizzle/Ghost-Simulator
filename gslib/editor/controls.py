
from gslib import game
from gslib.ui import button
from gslib.ui import drop_down_list


# A bunch of functions to create immediate-mode controls.
# They should be called once every time you need to redraw the controls.


class Container(object):

    def __init__(self, things):
        self.things = things
        self.x = 0
        self.y = 0

    @property
    def _unique_name(self):
        return ((getattr(self, 'name') if hasattr(self, 'name') else "")
                + (getattr(self, 'obj').__class__.__name__ if hasattr(self, 'obj') else "")
                + (getattr(self, 'attr').__class__.__name__ if hasattr(self, 'attr') else "")
                + self.__class__.__name__)

    @property
    def highlighted(self):
        return game.highlighted_control == self._unique_name

    @highlighted.setter
    def highlighted(self, v):
        if self.highlighted and not v:
            game.highlighted_control = ""
        elif v and not self.highlighted:
            game.highlighted_control = self._unique_name

    def do_layout(self):
        # performs layout of sub-controls based on .x, .y
        pass

    @property
    def width(self):
        return NotImplementedError()

    @property
    def height(self):
        return NotImplementedError()

    def get(self):
        l = []
        for t in self.things:
            if hasattr(t, 'get'):
                l.extend(t.get())
            else:
                l.append(t)
        return l


class HLayout(Container):

    def __init__(self, things):
        super(HLayout, self).__init__(things)

    def do_layout(self):
        add_x = 0
        for t in self.things:
            t.x = self.x + add_x
            t.y = self.y
            t.do_layout()
            add_x += t.width

    @property
    def width(self):
        return reduce(lambda accum, thing: accum + thing.width, self.things, 0)

    @property
    def height(self):
        return reduce(lambda accum, thing: thing.height if thing.height > accum else accum, self.things, 0)


class VLayout(Container):

    def __init__(self, things):
        super(VLayout, self).__init__(things)

    def do_layout(self):
        add_y = 0
        for t in self.things:
            t.x = self.x
            t.y = self.y + add_y
            t.do_layout()
            add_y += t.height

    @property
    def width(self):
        return reduce(lambda accum, thing: accum + thing.width, self.things, 0)

    @property
    def height(self):
        return reduce(lambda accum, thing: thing.height if thing.height > accum else accum, self.things, 0)


class RGButton(button.Button):

    def __init__(self, owner, function, pos=(0, 0), text=u"", size=(100, 20), green=False, **kwargs):
        if green:
            super(RGButton, self).__init__(owner, function, size=size, pos=pos, border_color=(0, 200, 0),
                                           border_width=3, color=(0, 200, 0), text=text, **kwargs)
        else:
            super(RGButton, self).__init__(owner, function, size=size, pos=pos, border_color=(120, 50, 80),
                                           border_width=3, color=(120, 0, 0), text=text, **kwargs)

    def get(self):
        return [self]

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, v):
        self.pos = (v, self.pos[1])

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, v):
        self.pos = (self.pos[0], v)

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, v):
        self.size = (v, self.size[1])

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, v):
        self.size = (self.size[0], v)

    def do_layout(self):
        pass


class RGDropDownList(drop_down_list.DropDownList):

    def __init__(self, *args, **kwargs):
        super(RGDropDownList, self).__init__(*args, **kwargs)

    def get(self):
        return [self]

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, v):
        self.pos = (v, self.pos[1])

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, v):
        self.pos = (self.pos[0], v)

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, v):
        self.size = (v, self.size[1])

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, v):
        self.size = (self.size[0], v)

    def do_layout(self):
        pass
