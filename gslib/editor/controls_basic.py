
import collections
import pyglet.window.key as Pkey

from gslib import game
from gslib.editor.controls import *


class IntControl(HLayout):

    def __init__(self, name, obj, attr):
        self.name = name
        self.obj = obj
        self.attr = attr

        super(IntControl, self).__init__([
            RGButton(self, None, text=name),
            RGButton(self, lambda: self._add_minus(False), text='-', size=(20, 20)),
            RGButton(self, None, text=str(getattr(self.obj, self.attr)), size=(50, 20)),
            RGButton(self, lambda: self._add_minus(True), text='+', size=(20, 20))
        ])

    def _add_minus(self, positive):
        inc = 1
        if game.key_controller.keys[Pkey.LSHIFT] or game.key_controller.keys[Pkey.RSHIFT]:
            inc = 10
        if game.key_controller.keys[Pkey.LCTRL] or game.key_controller.keys[Pkey.RCTRL]:
            inc = 50
        if not positive:
            inc = -inc
        setattr(self.obj, self.attr, getattr(self.obj, self.attr) + inc)


class GameObjectControl(HLayout):

    def __init__(self, name, obj, attr):
        self.name = name
        self.obj = obj
        self.attr = attr

        super(GameObjectControl, self).__init__([
            RGButton(self, None, text=name),
            RGButton(self, self._pick, size=(50, 20), green=self.highlighted, text="Pick"),
        ])

    def _finish_pick(self, o_name):
        self.highlighted = False
        setattr(self.obj, self.attr, o_name)

    def _pick(self):
        # are they actually unclicking the button?
        if self.highlighted:
            self.highlighted = False
        else:
            self.highlighted = True
            game.mouse_controller.pick_object(self._finish_pick)


class BoolControl(HLayout):

    def __init__(self, name, obj, attr):
        self.name = name
        self.obj = obj
        self.attr = attr

        super(BoolControl, self).__init__([
            RGButton(self, None, text=name),
            RGButton(self, self._toggle, size=(50, 20), text=u"\u2713" if getattr(self.obj, self.attr) else "x",
                     green=getattr(self.obj, self.attr))
        ])

    def _toggle(self):
        setattr(self.obj, self.attr, not getattr(self.obj, self.attr))


class StringDropDown(HLayout):

    def __init__(self, name, obj, attr):
        self.name = name
        self.obj = obj
        self.attr = attr

        current = getattr(self.obj, self.attr)
        dd = collections.OrderedDict()
        try:
            l = self.obj.get_autocomplete(self.attr)
            for dkey in l:
                dd[dkey] = dkey
        except:
            # no autocomplete? that's fine.
            dd.clear()
        dd[current] = current

        super(StringDropDown, self).__init__([
            RGDropDownList(self, dd, None, size=(250, 20))
        ])

        try:
            self.things[0].set_to_value(getattr(self.obj, self.attr))
        except:
            setattr(self.obj, self.attr, None)
            self.things[0].set_to_default()

        self.things[0].function = self._choose

    def _choose(self):
        setattr(self.obj, self.attr, self.things[0].selected)
