import os.path
import sys

def fallback_files(target, *fnames):
    for fname in fnames:
        if os.path.exists(fname):
            return fname
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
TEXTBOX_TEST = 8
KEYBIND_MENU = 9
KEYBIND_CAPTURE = 10

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

ANIM_UPIDLE = 0
ANIM_RIGHTIDLE = 1
ANIM_DOWNIDLE = 2
ANIM_LEFTIDLE = 3
ANIM_UPWALK = 4
ANIM_RIGHTWALK = 5
ANIM_DOWNWALK = 6
ANIM_LEFTWALK = 7

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

MUSIC_DIR = fallback_files("music dir", "music", os.path.join(sys.prefix, "gs-music"))
SOUND_DIR = fallback_files("sound dir", "sound", os.path.join(sys.prefix, "gs-sound"))
VIDEO_DIR = fallback_files("video dir", "video", os.path.join(sys.prefix, "gs-video"))
CHARACTER_DIR = fallback_files("characters dir", "characters", os.path.join(sys.prefix, "gs-chars"))
TILES_DIR = fallback_files("tiles dir", "tiles", os.path.join(sys.prefix, 'gs-tiles'))
CREDITS_FILE = fallback_files("credits file", "credits.txt", os.path.join(sys.prefix, 'gs-data', 'credits.txt'))
SKILLS_FILE = fallback_files("skills file", "skills.json", os.path.join(sys.prefix, 'gs-data', 'skills.json'))
KEYMAP_FILE = fallback_files("keymap file", "keymap.txt", os.path.join(sys.prefix, 'gs-data', 'keymap.txt'))
OPTIONS_FILE = fallback_files("options file", "options.txt", os.path.join(sys.prefix, 'gs-data', 'options.txt'))

LEARNT_SKILL_COLOUR = (0, 150, 0)
CAN_BE_LEARNT_COLOUR = (0, 0, 150)
UNLEARNABLE_COLOUR = (150, 0, 0)

INITIAL_SOUND_VOLUME = 0.2
INITIAL_MUSIC_VOLUME = 0.2

FONT = 'papyrus, helvetica'
