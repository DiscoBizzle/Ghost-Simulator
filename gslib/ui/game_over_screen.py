from __future__ import absolute_import, division, print_function

import pyglet

from gslib import window
from gslib.constants import *


class GameOverScreen(pyglet.event.EventDispatcher):
    def __init__(self):
        self._batch = pyglet.graphics.Batch()

        self._game_over_txt1 = pyglet.text.Label(u"GAME OVER", FONT, 80, color=(255, 255, 255, 255), anchor_x='left',
                                                 anchor_y='bottom', align='center', batch=self._batch)

        self._game_over_txt2 = pyglet.text.Label(u"press esc scrub", FONT, 20, color=(255, 255, 255, 255),
                                                 anchor_x='left', anchor_y='bottom', align='center', batch=self._batch)

        self.on_resize(window.width, window.height)

    def draw(self):
        self._batch.draw()

    def on_resize(self, width, height):
        self._game_over_txt1.x = (width - self._game_over_txt1.content_width) // 2
        self._game_over_txt1.y = (height - self._game_over_txt1.content_height) // 2

        self._game_over_txt2.x =\
            (width - self._game_over_txt2.content_width) // 2
        self._game_over_txt2.y =\
            (height - self._game_over_txt2.content_height - self._game_over_txt1.content_height) // 2

    def start(self):
        self.on_resize(window.width, window.height)
        window.push_handlers(self)

    def stop(self):
        window.remove_handlers(self)
        self.dispatch_event('on_game_over_close')

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.stop()
            return pyglet.event.EVENT_HANDLED


GameOverScreen.register_event_type('on_game_over_close')
