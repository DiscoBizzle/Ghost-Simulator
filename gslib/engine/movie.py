from __future__ import absolute_import, division, print_function

import os.path

import pyglet

from gslib import window
from gslib.constants import *


class MoviePlayer(pyglet.event.EventDispatcher):
    def __init__(self):
        self._player = None

        # TODO: THIS IS A HACK TO WORK AROUND on_eos BEING BROKEN
        self._playing = False

    def _toggle_pause(self):
        if self._playing:
            self._player.pause()
            self._playing = False
        else:
            self._player.play()
            self._playing = True

    def start(self, movie):
        try:
            video_source = pyglet.media.load(os.path.join(VIDEO_DIR, movie))
        except IOError:
            print(u"Video not found: {}".format(movie))
            self.dispatch_event('on_movie_end')
            return
        self._player = pyglet.media.Player()
        self._player.queue(video_source)
        self._player.push_handlers(on_eos=self.stop)
        self._player.play()
        self._playing = True
        window.push_handlers(self)

    def stop(self):
        window.remove_handlers(self)
        if self._player is not None:
            self._player.pause()
            self._player.remove_handlers(on_eos=self.stop)
            self._player = None
        self._playing = False
        self.dispatch_event('on_movie_end')

    def draw(self):

        # TODO: THIS IS A HACK TO WORK AROUND on_eos BEING BROKEN
        if not self._player.playing and self._playing:
            self.stop()
            return

        if self._player is not None:
            self._player.get_texture().blit(0, 0, width=window.width, height=window.height)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.stop()
            return pyglet.event.EVENT_HANDLED
        elif symbol == pyglet.window.key.SPACE:
            self._toggle_pause()
            return pyglet.event.EVENT_HANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            self._toggle_pause()
            return pyglet.event.EVENT_HANDLED

MoviePlayer.register_event_type('on_movie_end')
