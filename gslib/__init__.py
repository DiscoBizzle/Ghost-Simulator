from __future__ import absolute_import, division, print_function

import pyglet

from gslib import class_proxy
from gslib.options_container import Options
from gslib.constants import *


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(GameWindow, self).__init__(*args, **kwargs)
        options.push_handlers(self)

    # disable the default pyglet key press handler
    def on_key_press(self, symbol, modifiers):
        pass

    def on_resize(self, width, height):
        super(GameWindow, self).on_resize(width, height)
        options['resolution'] = (width, height)

    def on_option_change(self, k, old_value, new_value):
        if k == 'vsync':
            self.set_vsync(new_value)
        elif k == 'fullscreen':
            self.set_fullscreen(fullscreen=new_value)
            options['resolution'] = self.get_size()
        elif k == 'resolution':
            if self.fullscreen:
                self.set_fullscreen(width=new_value[0], height=new_value[1])
            else:
                self.set_size(*new_value)


options = Options(DEFAULT_OPTIONS)
options.load_options()

window = GameWindow(width=options['resolution'][0], height=options['resolution'][1], resizable=True,
                    vsync=options['vsync'], fullscreen=options['fullscreen'])

game = class_proxy.Proxy()

