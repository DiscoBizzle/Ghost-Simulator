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

    def on_option_change(self, key, value):
        if key == 'vsync':
            self.set_vsync(value)
        elif key == 'fullscreen':
            self.set_fullscreen(fullscreen=value)
            options['resolution'] = self.get_size()
        elif key == 'resolution':
            if self.fullscreen:
                self.set_fullscreen(width=value[0], height=value[1])
            else:
                self.set_size(*value)


options = Options(DEFAULT_OPTIONS)
options.load_options()

window = GameWindow(width=options['resolution'][0], height=options['resolution'][1], resizable=True,
                    vsync=options['vsync'], fullscreen=options['fullscreen'])

game = class_proxy.Proxy()
