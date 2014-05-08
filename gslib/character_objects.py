import gslib.character_functions as fear_functions
from gslib import character
from gslib.character import Character
from gslib.constants import *
from gslib import sprite
from pyglet import image
import random


# Please make these only require game_class by default (for purposes of editor)

class SmallDoor(Character):
    def __init__(self, game_class, x=0, y=0, stats=None):
        super(SmallDoor, self).__init__(game_class, x, y, 32, 32, stats, sprite_sheet='small_door_sheet.png',
                                        sprite_width=32, sprite_height=32)

        self.max_speed = 0
        self.current_speed = 0
        self.normal_speed = 0

        self.scared_of = []
        self.fears = ['doors']

        self.states = {'0': {'animation_state': 0, 'collision_weight': 0},
                       '1': {'animation_state': 2, 'collision_weight': 100}}
        self.state_index = '1'  # make sure you set this after the states are defined, so the properties get updated

        self.possessed_function = [fear_functions.flip_state(self)]
        self.unpossessed_function = [fear_functions.flip_state(self)]

        self.stats = {'image_name': os.path.join(CHARACTER_DIR, 'small_door_sheet.png'), 'name': u'Small Door', 'age': random.randint(0, 500)}
        self.info_sheet = character.draw_info_sheet(self.stats)

    def _update_animation(self):
        pass

    def _create_animations(self):
        seq_cols = self.sprite_sheet.width // self.sprite_width
        seq_rows = self.sprite_sheet.height // self.sprite_height
        seq = image.ImageGrid(self.sprite_sheet, seq_rows, seq_cols)
        self._animations += seq[::6]
        self.sprite = sprite.Sprite(self._animations[self._animation_state])


class Dude(Character):
    def __init__(self, game_class, x=0, y=0, stats=None):
        if stats is None:
            stat = character.gen_character()
        else:
            stat = stats
        super(Dude, self).__init__(game_class, x, y, 16, 16, stat, sprite_sheet='DudeSheet.png', sprite_width=16,
                                   sprite_height=32)
        self.normal_speed = 0

        self.direction = DOWN
