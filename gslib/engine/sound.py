from __future__ import absolute_import, division, print_function

import os

import pyglet

from gslib import options
from gslib.constants import *


class Sound(object):
    def __init__(self):

        self.music_playing = None
        self.sound_playing = set()
        self.music_dict = None
        self.sound_dict = None

        self.load_all_sounds()
        self.load_all_music()

        options.push_handlers(self)

    def on_option_change(self, key, value):
        if key == 'music_volume':
            if self.music_playing is not None:
                self.music_playing.volume = value
        elif key == 'sound_volume':
            for s in self.sound_playing:
                s.volume = value

    def load_all_sounds(self):
        sound_dict = {}
        for f in os.listdir(SOUND_DIR):
            if f[-4:] in (".ogg", ".wav"):
                sound_dict[f[:-4]] = pyglet.media.load(os.path.join(SOUND_DIR, f), streaming=False)
        self.sound_dict = sound_dict

    def load_all_music(self):
        music_dict = {}
        for f in os.listdir(MUSIC_DIR):
            if f[-4:] in (".ogg", ".wav"):
                music_dict[f[:-4]] = pyglet.media.load(os.path.join(MUSIC_DIR, f))
        self.music_dict = music_dict

    def play_music(self, name):
        if self.music_playing is not None:
            self.music_playing.pause()
        handler = self.music_dict[name].play()
        handler.volume = options['music_volume']
        handler.name = name
        self.music_playing = handler

    def play_sound(self, name):
        handler = self.sound_dict[name].play()
        handler.volume = options['sound_volume']
        handler.name = name
        self.sound_playing.add(handler)
        handler.push_handlers(on_eos=(lambda: self.sound_eos(handler)))

    def sound_eos(self, handler):
        # pop handlers so handler can be garbage collected
        handler.pop_handlers()
        self.sound_playing.remove(handler)
