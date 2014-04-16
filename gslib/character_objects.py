import gslib.character_functions as fear_functions
import gslib.character as character
from gslib.character import Character
from gslib.constants import *
import random


# Please make these only require game_class by default (for purposes of editor)

class SmallDoor(Character):
    def __init__(self, game_class, x=0, y=0, stats=None):
        Character.__init__(self, game_class, x, y, TILE_SIZE, TILE_SIZE, stats, sprite_sheet='small_door_sheet.png')
        self.max_speed = 0
        self.current_speed = 0
        self.normal_speed = 0

        self.scared_of = []
        self.fears = ['doors']

        self.max_frames = 0
        self.sprite_height = 32
        self.sprite_width = 32
        self.states = {0: {'animation_state': 0, 'collision_weight': 0},
                       1: {'animation_state': 2, 'collision_weight': 100}}
        self.state_index = 1  # make sure you set this after the states are defined, so the properties get updated

        print
        self.possessed_function = [fear_functions.flip_state(self)]
        self.unpossessed_function = [fear_functions.flip_state(self)]

        self.stats = {'image_name': os.path.join(CHARACTER_DIR, 'small_door_sheet.png'), 'name': u'Small Door', 'age': random.randint(0, 500)}
        self.info_sheet = self.draw_info_sheet()


class Dude(Character):
    def __init__(self, game_class, x=0, y=0, stats=character.gen_character()):
        Character.__init__(self, game_class, x, y, 16, 16, stats)
