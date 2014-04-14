import os
import random

import pyglet
import time

from gslib.constants import *


class Sound(object):
    def __init__(self):
        # TODO remove handler from currently playing when finished playing by pushing events

        self._music_volume = INITIAL_MUSIC_VOLUME
        self._sound_volume = INITIAL_SOUND_VOLUME
        self.music_playing = []
        self.sound_playing = []
        self.music_list = []
        self.sound_dict = {}

        self.load_all_sounds()
        self.load_all_music()

    def get_music_volume(self):
        return self._music_volume

    def set_music_volume(self, val):
        self._music_volume = val
        for m in self.music_playing:
            m.volume = val
    music_volume = property(get_music_volume, set_music_volume)

    def get_sound_volume(self):
        return self._music_volume

    def set_sound_volume(self, val):
        self._sound_volume = val
        for s in self.sound_playing:
            s.volume = val
    sound_volume = property(get_sound_volume, set_sound_volume)

    def load_all_sounds(self):
        sound_dict = {}
        for f in os.listdir(SOUND_DIR):
            if f[-4:] in (".ogg", ".wav"):
                sound_dict[f[:-4]] = pyglet.media.load(os.path.join(SOUND_DIR, f), streaming=False)
        self.sound_dict = sound_dict

    def load_all_music(self):
        music_list = []
        for f in os.listdir(MUSIC_DIR):
            if f[-4:] in (".ogg", ".wav"):
                music_list.append(pyglet.media.load(os.path.join(MUSIC_DIR, f)))
        self.music_list = music_list

    def start_next_music(self):
        handler = random.choice(self.music_list).play()
        handler.volume = self._music_volume
        self.music_playing.append(handler)

    def play_sound(self, name):
        handler = self.sound_dict[name].play()
        handler.volume = self._sound_volume
        self.sound_playing.append(handler)