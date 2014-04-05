__author__ = 'Michael'

import os
import pygame
import random
from Constants import *

def load_all_sounds():
    sound_dict = {}
    for f in os.listdir(SOUND_DIR):
        if f[-4:] in (".ogg", ".wav"):
            sound_dict[f[:-4]] = pygame.mixer.Sound(os.path.join(SOUND_DIR, f))

    return sound_dict

def get_music_list():
    musicList = []
    for f in os.listdir(MUSIC_DIR):
        if f[-4:] in (".ogg", ".wav"):
            musicList.append(os.path.join(MUSIC_DIR, f))
    return musicList

def start_next_music(musicList):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(random.choice(musicList))
    pygame.mixer.music.play()

