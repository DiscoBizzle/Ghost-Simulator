import os
import random

import pyglet
import time

from gslib.constants import *


class Sound(object):
    def __init__(self, game):
        # TODO remove handler from currently playing when finished playing by pushing events

        self.game = game

        self.music_playing = []
        self.sound_playing = []
        self.music_list = []
        self.sound_dict = {}

        self.load_all_sounds()
        self.load_all_music()

        self.game.options.push_handlers(self)

    def on_option_change(self, k, old_value, new_value):
        if k == 'music_volume':
            for m in self.music_playing:
                m.volume = new_value
        elif k == 'sound_volume':
            for s in self.sound_playing:
                s.volume = new_value

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
        handler.volume = self.game.options['music_volume']
        self.music_playing.append(handler)

    def play_sound(self, name):
        handler = self.sound_dict[name].play()
        handler.volume = self.game.options['sound_volume']
        self.sound_playing.append(handler)