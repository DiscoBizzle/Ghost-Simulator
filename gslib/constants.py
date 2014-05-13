import os.path
import sys

__all__ = ['STARTUP', 'MAIN_MENU', 'MAIN_GAME', 'CUTSCENE', 'GAME_OVER', 'SKILLS_SCREEN', 'CREDITS', 'OPTIONS_MENU',
           'KEYBIND_MENU', 'KEYBIND_CAPTURE', 'EDITOR', 'TICKS_PER_SEC', 'GAME_WIDTH', 'GAME_HEIGHT', 'LEVEL_WIDTH',
           'LEVEL_HEIGHT', 'TILE_SIZE', 'SPRITE_WIDTH', 'SPRITE_HEIGHT', 'SPRITE_COLL_WIDTH', 'SPRITE_COLL_HEIGHT',
           'SELECTION_TOLERANCE', 'UP', 'RIGHT', 'DOWN', 'LEFT', 'ANIM_UPIDLE', 'ANIM_RIGHTIDLE', 'ANIM_DOWNIDLE',
           'ANIM_LEFTIDLE', 'ANIM_UPWALK', 'ANIM_RIGHTWALK', 'ANIM_DOWNWALK', 'ANIM_LEFTWALK', 'TICKS_PER_FRAME',
           'TICKS_PER_CHAR', 'TB_INACTIVE', 'TB_STARTING', 'TB_WRITING', 'TB_ACTIVE', 'TB_CLOSING', 'TB_OPEN_SPEED',
           'MAX_FEAR', 'START_FEAR', 'FEAR_PER_STEP', 'FEAR_PER_TICK', 'POSSESSION_RANGE', 'FEAR_COLLECTION_RADIUS',
           'MUSIC_DIR', 'SOUND_DIR', 'VIDEO_DIR', 'CHARACTER_DIR', 'TILES_DIR', 'CREDITS_FILE', 'SKILLS_FILE',
           'KEYMAP_FILE', 'OPTIONS_FILE', 'SAVE_DIR', 'LEARNT_SKILL_COLOR', 'CAN_BE_LEARNT_COLOR', 'UNLEARNABLE_COLOR',
           'INITIAL_SOUND_VOLUME', 'INITIAL_MUSIC_VOLUME', 'FONT', 'DEFAULT_OPTIONS', 'DIALOGUE_DIR', 'SLEEP_TARGET']


def fallback_files(target, required, *fnames):
    for fname in fnames:
        if os.path.exists(fname):
            return fname
    if not required:
        return fnames[0]
    raise Exception("Couldn't find {}".format(target))

# Game States
STARTUP = 0
MAIN_MENU = 1
MAIN_GAME = 2
CUTSCENE = 3
GAME_OVER = 4
SKILLS_SCREEN = 5
CREDITS = 6
OPTIONS_MENU = 7
KEYBIND_MENU = 8
KEYBIND_CAPTURE = 9
EDITOR = 10

TICKS_PER_SEC = 35
SLEEP_TARGET = 100

GAME_WIDTH = 1280
GAME_HEIGHT = 720
LEVEL_WIDTH, LEVEL_HEIGHT = 1280, 640
TILE_SIZE = 32

SPRITE_WIDTH = 16
SPRITE_HEIGHT = 32
SPRITE_COLL_WIDTH = 8
SPRITE_COLL_HEIGHT = 8

SELECTION_TOLERANCE = 10

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

ANIM_UPIDLE = 7
ANIM_RIGHTIDLE = 6
ANIM_DOWNIDLE = 5
ANIM_LEFTIDLE = 4
ANIM_UPWALK = 3
ANIM_RIGHTWALK = 2
ANIM_DOWNWALK = 1
ANIM_LEFTWALK = 0

TICKS_PER_FRAME = 8  # number of game frames for each sprite animation frame
TICKS_PER_CHAR = 1 #the rate at which characters are "typed" in textboxes

#constants for the textbox
TB_INACTIVE = 0
TB_STARTING = 1
TB_WRITING = 2
TB_ACTIVE = 3
TB_CLOSING = 4
TB_OPEN_SPEED = 3

MAX_FEAR = 2500
START_FEAR = 1000
FEAR_PER_STEP = 0 #1.5
FEAR_PER_TICK = 0 #3.0
POSSESSION_RANGE = 50
FEAR_COLLECTION_RADIUS = 300

MUSIC_DIR = fallback_files("music dir", True, "music", os.path.join(sys.prefix, "gs-music"))
SOUND_DIR = fallback_files("sound dir", True, "sound", os.path.join(sys.prefix, "gs-sound"))
VIDEO_DIR = fallback_files("video dir", True, "video", os.path.join(sys.prefix, "gs-video"))
CHARACTER_DIR = fallback_files("characters dir", True, "characters", os.path.join(sys.prefix, "gs-chars"))
TILES_DIR = fallback_files("tiles dir", True, "tiles", os.path.join(sys.prefix, 'gs-tiles'))
CREDITS_FILE = fallback_files("credits file", True, "credits.txt", os.path.join(sys.prefix, 'gs-data', 'credits.txt'))
SKILLS_FILE = fallback_files("skills file", True, "skills.json", os.path.join(sys.prefix, 'gs-data', 'skills.json'))
KEYMAP_FILE = fallback_files("keymap file", True, "keymap.txt", os.path.join(sys.prefix, 'gs-data', 'keymap.txt'))
OPTIONS_FILE = fallback_files("options file", False, "options.txt", os.path.join(sys.prefix, 'gs-data', 'options.txt'))
SAVE_DIR = fallback_files("save dir", True, "save", os.path.join(sys.prefix, 'gs-save'))
DIALOGUE_DIR = fallback_files("dialogue dir", True, "story", os.path.join(sys.prefix, 'gs-story'))

LEARNT_SKILL_COLOR = (0, 150, 0)
CAN_BE_LEARNT_COLOR = (0, 0, 150)
UNLEARNABLE_COLOR = (150, 0, 0)

INITIAL_SOUND_VOLUME = 1.0
INITIAL_MUSIC_VOLUME = 1.0

FONT = ['Helvetica']

DEFAULT_OPTIONS = {'FOV': True, 'VOF': False, 'torch': False, 'menu_scale': False, 'vsync': False,
                   'sound_volume': INITIAL_SOUND_VOLUME, 'music_volume': INITIAL_MUSIC_VOLUME,
                   'fullscreen': False, 'resolution': (GAME_WIDTH, GAME_HEIGHT), 'VOF_opacity': 128,
                   'scheduler_frequency': 100}
