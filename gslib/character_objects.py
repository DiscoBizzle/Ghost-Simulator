from __future__ import absolute_import, division, print_function

import os.path

# import gslib.character_functions as fear_functions
from gslib import character_functions
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
        self.fears.append('doors')

        self.states = {'0': {'animation_state': 0, 'collision_weight': 0},
                       '1': {'animation_state': 2, 'collision_weight': 100}}
        self.state_index = '1'  # make sure you set this after the states are defined, so the properties get updated

        self.possessed_function = [character_functions.flip_state(self)]
        self.unpossessed_function = [character_functions.flip_state(self)]

        self.stats = {'image_name': os.path.join(CHARACTERS_DIR, 'small_door_sheet.png'), 'name': u'Small Door', 'age': random.randint(0, 500)}
        self.info_sheet = character.draw_info_sheet(self.stats)

    def _update_animation(self):
        pass

    def _create_animations(self):
        seq_cols = self.sprite_sheet.width // self.sprite_width
        seq_rows = self.sprite_sheet.height // self.sprite_height
        seq = image.ImageGrid(self.sprite_sheet, seq_rows, seq_cols)
        self._animations += seq[::6]
        self.sprite = sprite.Sprite(self._animations[self._animation_state])

    def activate(self):
        self.state_index = str((int(self.state_index) + 1) % len(self.states))


class Dude(Character):
    def __init__(self, game_class, x=0, y=0, stats=None):
        if stats is None:
            stat = character.gen_character()
        else:
            stat = stats
        super(Dude, self).__init__(game_class, x, y, 16, 16, stat, sprite_sheet='DudeSheet.png', sprite_width=16,
                                   sprite_height=32)
        self.normal_speed = 1
        self.feared_speed = 5

        self.feared_function.append(character_functions.panic(self))
        self.idle_functions.append(character_functions.stand_still(self))

        self.direction = DOWN


class Bomb(Character):
    def __init__(self, game, x=0, y=0):
        super(Bomb, self).__init__(game, x, y, 32, 32, sprite_width=32, sprite_height=32, sprite_sheet='bomb.png')

        self.normal_speed = 0
        self.feared_speed = 0

        self.is_touched_function.append(character_functions.activate_on_fire(self))

        self.states = {'normal': {'animation_state': 0},
                       'exploded': {'animation_state': 1}}

        self.stats = {'name': 'La Bomba', 'age': 0, 'image_name': os.path.join(CHARACTER_DIR, 'bomb.png')} # have to do stats manually atm for reason for character sheet

    def activate(self):
        self.state_index = 'exploded'


class SpriteBoss(Character):
    def __init__(self, game, x=0, y=0):
        super(SpriteBoss, self).__init__(game, x, y, 256, 256, sprite_width=256, sprite_height=256, sprite_sheet='Sprite_top.png')

        self.normal_speed = 0
        self.feared_speed = 0

        self.stats = {'name': 'Sprite.', 'age': 55, 'image_name': os.path.join(CHARACTER_DIR, 'Sprite_top.png')} # have to do stats manually atm for reason for character sheet



possible_characters = {'Small Door': SmallDoor,
                       'Dude': Dude,
                       'Bomb': Bomb,
                       'Sprite Boss': SpriteBoss}
