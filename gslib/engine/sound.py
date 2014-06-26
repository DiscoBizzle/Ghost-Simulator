from __future__ import absolute_import, division, print_function

import os

import pyglet

from gslib import options
from gslib.constants import *


def load_all_music():
    music_dict = {}
    for f in os.listdir(MUSIC_DIR):
        if f[-4:] in (".ogg", ".wav"):
            music_dict[f[:-4]] = os.path.join(MUSIC_DIR, f)
    return music_dict


def load_all_sounds():
    sound_dict = {}
    for f in os.listdir(SOUND_DIR):
        if f[-4:] in (".ogg", ".wav"):
            sound_dict[f[:-4]] = pyglet.media.load(os.path.join(SOUND_DIR, f), streaming=False)
    return sound_dict


class Sound(object):
    def __init__(self):

        self.music_player = None
        self.current_music = None
        self.sound_playing = set()
        self.music_dict = load_all_music()
        self.sound_dict = load_all_sounds()

        options.push_handlers(self)

    def on_option_change(self, key, value):
        if key == 'music_volume':
            if self.music_player is not None:
                self.music_player.volume = value
        elif key == 'sound_volume':
            for player in self.sound_playing:
                player.volume = value

    def play_music(self, name):
        if self.music_player is not None:
            self.music_player.delete()
        player = pyglet.media.Player()
        player.volume = options['music_volume']
        player.eos_action = pyglet.media.Player.EOS_LOOP
        player.queue(pyglet.media.load(self.music_dict[name]))
        player.play()
        self.current_music = name
        self.music_player = player

    def play_sound(self, name):
        player = pyglet.media.Player()
        player.queue(self.sound_dict[name])
        player.volume = options['sound_volume']
        player.push_handlers(on_eos=(lambda: self._sound_eos(player)))
        player.play()
        self.sound_playing.add(player)

    def _sound_eos(self, player):
        # pop handlers so player can be garbage collected
        player.pop_handlers()
        player.delete()
        self.sound_playing.remove(player)
