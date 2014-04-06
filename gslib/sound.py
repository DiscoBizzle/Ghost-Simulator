import os
import random

import pygame

from gslib.constants import *

def load_all_sounds():
    sound_dict = {}
    for f in os.listdir(SOUND_DIR):
        if f[-4:] in (".ogg", ".wav"):
            sound_dict[f[:-4]] = pygame.mixer.Sound(os.path.join(SOUND_DIR, f))
    for sound in sound_dict.itervalues():
        sound.set_volume(INITIAL_SOUND_VOLUME)
    return sound_dict


def get_music_list():
    musicList = []
    pygame.mixer.music.set_volume(INITIAL_MUSIC_VOLUME)
    for f in os.listdir(MUSIC_DIR):
        if f[-4:] in (".ogg", ".wav"):
            musicList.append(os.path.join(MUSIC_DIR, f))
    return musicList


def start_next_music(musicList):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(random.choice(musicList))
    pygame.mixer.music.play()

