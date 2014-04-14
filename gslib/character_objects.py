import gslib.fear_functions as fear_functions
from gslib.character import Character
from gslib.constants import *


class SmallDoor(Character):
    def __init__(self, game_class, x, y, stats):
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

        self.possessed_function = fear_functions.flip_state(self)
        self.unpossessed_function = fear_functions.flip_state(self)