__author__ = 'Michael'

import os
import pygame
import random

def load_all_sounds():
    sound_dict = {}
    for f in os.listdir("sounds"):
        if '.ogg' == f[-4:]:
            sound_dict[f[:-4]] = pygame.mixer.Sound(os.path.join("Sounds", f))
        elif '.wav' == f[-4:]:
            sound_dict[f[:-4]] = pygame.mixer.Sound(os.path.join("Sounds", f))

    return sound_dict

def get_music_list():
    musicList = []
    for f in os.listdir("music"):
        if '.ogg' == f[-4:]:
            musicList.append(os.path.join("Music", f))
        elif '.wav' == f[-4:]:
            musicList.append(os.path.join("Music", f))
    return musicList

def start_next_music(musicList):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(random.choice(musicList))
    pygame.mixer.music.play()

