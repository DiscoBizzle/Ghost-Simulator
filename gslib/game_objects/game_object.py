from __future__ import absolute_import, division, print_function

import os.path
import collections

from pyglet import image

from gslib.constants import *
from gslib.engine import sprite, rect


class FearsList(collections.MutableSequence):
    def __init__(self, owner, *args):
        self.owner = owner
        self.list = list()
        self.extend(list(args))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, item):
        return self.list[item]

    def __delitem__(self, key):
        val = self.list[key]
        self.owner.game_class.map.fears_dict[v].remove(self.owner)
        del self.list[key]

    def __setitem__(self, key, value):
        self.owner.game_class.map.fears_dict[self.list[key]].remove(self.owner)
        if not self.owner in self.owner.game_class.map.fears_dict[value]:
            self.owner.game_class.map.fears_dict[value].append(self.owner)
        self.list[key] = value

    def insert(self, index, value):
        if not self.owner in self.owner.game_class.map.fears_dict[value]:
            self.owner.game_class.map.fears_dict[value].append(self.owner)
        self.list.insert(index, value)

    def __str__(self):
        return str(self.list)


class GameObject(object):
    def __init__(self, game_class, x, y, w, h, sprite_sheet, sprite_width, sprite_height):
        """
        To add an object to a map:
        map.objects['object name'] = object

        Object states:
        Each state has a name (consider using integers if you want to advance through them sequentially)
        Each state is a dict of properties that the object will update to when state_index is changed to that state name
        Ensure that these properties are spelt correctly!
        To change state elsewhere, just set object.state_index = <state_name_here>, properties will automatically update

        Flair:
        Flair is a dict of 'name': (surface, position (relative to object centre)) to additionally render attached to sprite
        E.g. Hats, speech bubbles.

        Collision:
        Each object has a collision_weight.
        Objects can only push objects with equal or less weight.
        Objects can only push a chain of objects up to their own weight.
        If an objects' collision weight is 0, it does not collide with objects.
        Collision rectangle updates automatically if you change obj dimensions (or coord).
        """
        self.game_class = game_class

        self.states = {'state1': {'max_speed': 1, 'fear_radius': 50},
                       'state2': {'max_speed': 5, 'fear_radius': 150}}
        self._state_index = 'state1'

        self._coord = (x, y)  # top left
        self._dimensions = (w, h)
        self.velocity = (0, 0)
        self.min_speed = 0
        self.current_speed = 0
        self.normal_speed = 0
        self.feared_speed = 0
        self.fear_radius = 50
        self.scared_of = []
        self.fears = FearsList(self)
        self.rect = rect.Rect(self.coord, self.dimensions)
        self.update_timer = 40
        self.fear_timer = 0
        self.scream_timer = 0
        self.fear = 0
        self.scream_thresh = 50

        #variables for animation
        self.sprite_sheet = image.load(os.path.join(CHARACTERS_DIR, sprite_sheet))
        self._animation_state = 0
        self.sprite_height = sprite_height
        self.sprite_width = sprite_width
        self._animations = []
        self._create_animations()
        self.sprite = sprite.Sprite(self._animations[self._animation_state], x=self._coord[0], y=self._coord[1])

        #trigger functions
        self.has_touched_function = []
        self.is_touched_function = []
        self.has_untouched_function = []
        self.is_untouched_function = []

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.highlight_radius = 20

        self.flair = {}
        self.collision_weight = 1  # set to 0 for no collision, can only push things that are lighter, or same weight

        self.cutscene_controlling = []

    @property
    def state_index(self):
        return self._state_index

    @state_index.setter
    def state_index(self, index):
        self._state_index = index
        for k, v in self.states[index].iteritems():
            setattr(self, k, v)

    @property
    def coord(self):
        return self._coord

    @coord.setter
    def coord(self, new):
        self._coord = new
        self.rect = rect.Rect(self.coord, self.dimensions)
        self.sprite.position = new
        self.game_class.object_collision_lookup.update_for(self)

    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, new):
        self._dimensions = new
        self.rect = rect.Rect(self.coord, self.dimensions)

    @property
    def animation_state(self):
        return self._animation_state

    @animation_state.setter
    def animation_state(self, val):
        if self._animation_state == val:
            return
        self._animation_state = val
        self.sprite.image = self._animations[self._animation_state]

    def update(self, dt):
        if self.cutscene_controlling:
            for cc in self.cutscene_controlling:
                cc.game_object_hook(self)
        else:
            v_x, v_y = 0, 0
            if self.move_down:
                v_y -= self.current_speed
                self.direction = DOWN
            if self.move_up:
                v_y += self.current_speed
                self.direction = UP
            if self.move_left:
                v_x -= self.current_speed
                self.direction = LEFT
            if self.move_right:
                v_x += self.current_speed
            self.velocity = (v_x, v_y)

        if not self.velocity == (0, 0):
            self.move()
            # self.rect = pygame.Rect(self.coord, self.dimensions)
        # self.apply_fear()
        self.get_feared()
        self._update_animation()

    def check_distance(self, other, distance):  # centre to centre distance is checked
        if self.get_distance_squared(other) < distance**2:
            return True
        else:
            return False

    def get_distance_squared(self, other):
        x = self.coord[0] + self.dimensions[0] / 2 - (other.coord[0] + other.dimensions[0] / 2)
        y = self.coord[1] + self.dimensions[1] / 2 - (other.coord[1] + other.dimensions[1] / 2)
        return x**2 + y**2

    def get_feared(self):
        if not hasattr(self, 'possessing'):  # checks if object is not a player as can't import player module
            self.fear = 0

        if len(self.scared_of) == 0:
            return

        for s in self.scared_of:
            for other in self.game_class.fears_dict[s]:
                if self.check_distance(other, self.fear_radius):
                    self.fear += 50
                    self.fear_timer = 5
                    self.feared_by_obj = other
                    self.feared_from_pos = other.coord

                    if self.fear >= self.scream_thresh:
                        # self.game_class.sound_handler.play_sound('scream')
                        self.scream_timer = 120
                    else:
                        self.scream_timer -= 1

    def remove_self_from_touching_list(self):
        to_remove = []
        for t in self.game_class.touching:
            if t[0] == self or t[1] == self:
                to_remove.append(t)
        for i in to_remove:
            self.game_class.touching.remove(i)


    def move(self):
        prev_pos = self.coord
        self.remove_self_from_touching_list()

        x_ticks, y_ticks = abs(self.velocity[0]), abs(self.velocity[1])
        move_x_per_tick, move_y_per_tick = 1 if self.velocity[0] > 0 else -1, 1 if self.velocity[1] > 0 else -1

        while x_ticks > 0 or y_ticks > 0:
            if x_ticks > 0:
                self.movePx(move_x_per_tick, 0)
                x_ticks -= 1
            if y_ticks > 0:
                self.movePx(0, move_y_per_tick)
                y_ticks -= 1

        for t in self.game_class.map.triggers.itervalues():
            t.check_zone_entry(self, prev_pos)

    def movePx(self, x_dir, y_dir):
        self.remove_self_from_touching_list()

        collision = False

        # collide againt map boundaries
        pro_pos = (self.coord[0] + x_dir, self.coord[1] + y_dir)
        pro_rect = rect.Rect(pro_pos, self.dimensions)
        if pro_pos[0] >= 0 and pro_pos[0] + self.dimensions[0] <= LEVEL_WIDTH and \
                        pro_pos[1] >= 0 and pro_pos[1] + self.dimensions[1] <= LEVEL_HEIGHT:
            pass
        else:
            collision = True

        # collision detection against map tiles
        # NOTE: assumes largest object w/ collision is 64x64 (i.e. 2x2 tiles)

        if pro_pos[0] >= 0 and pro_pos[1] >= 0:
            i = pro_pos[0] // TILE_SIZE  # get the index of the lower left tile
            j = pro_pos[1] // TILE_SIZE
        else:
            i = 0
            j = 0

        # check collision against the 9 possible tiles surrounding object
        for ni in range(i, i + 2):
            for nj in range(j, j + 2):
                if 0 <= ni < LEVEL_WIDTH // TILE_SIZE and 0 <= nj < LEVEL_HEIGHT // TILE_SIZE:
                    if self.game_class.map.coll_grid[nj][ni][0]:
                        # pygame.draw.rect(self.game_class.surface, (200, 0, 0), self.rect)
                        # pygame.draw.rect(self.game_class.surface, (0, 200, 0), self.game_class.map.grid[ni][nj].rect)
                        # pygame.display.update()
                        # time.sleep(0.1)
                        # TODO: make collision use (row,col)
                        if pro_rect.colliderect(self.game_class.map.coll_grid[nj][ni][1]):
                            collision = True
                            # print('collision!')

        search_rect = pro_rect.union(self.rect)

        # collision against other objects
        for o in set(self.game_class.object_collision_lookup.candidates_for(search_rect)):
            if not o is self:
                if o.collision_weight and self.collision_weight:  # check if obj collides at all
                    if pro_rect.colliderect(o.rect) and not self.rect.colliderect(o.rect):

                        if 1 + self.collision_weight < o.collision_weight:  # check if obj can be pushed by self
                            collision = True
                        else:  # push object
                            temp = o.collision_weight
                            o.collision_weight = (self.collision_weight - o.collision_weight) or -1  # allows to push chain of objs
                            collision = collision or o.movePx(x_dir, y_dir)  # collsion of self is dependent on whether obj collided
                            o.collision_weight = temp

                        if not (self, o) in self.game_class.touching:
                            self.game_class.touching.append((self, o))  # (toucher, touchee)

        if not collision:
            self.coord = pro_pos

        return collision

    def _update_animation(self):
        if self.velocity[1] == 0 and self.velocity[0] == 0:
            if self.animation_state == ANIM_DOWNWALK:
                self.animation_state = ANIM_DOWNIDLE
            elif self.animation_state == ANIM_RIGHTWALK:
                self.animation_state = ANIM_RIGHTIDLE
            elif self.animation_state == ANIM_UPWALK:
                self.animation_state = ANIM_UPIDLE
            elif self.animation_state == ANIM_LEFTWALK:
                self.animation_state = ANIM_LEFTIDLE
        else:
            if self.velocity[1] < 0:
                self.animation_state = ANIM_DOWNWALK
            elif self.velocity[1] > 0:
                self.animation_state = ANIM_UPWALK
            elif self.velocity[0] > 0:
                self.animation_state = ANIM_RIGHTWALK
            elif self.velocity[0] < 0:
                self.animation_state = ANIM_LEFTWALK

    def _create_animations(self):
        seq_cols = self.sprite_sheet.width // self.sprite_width
        seq_rows = self.sprite_sheet.height // self.sprite_height
        seq = image.ImageGrid(self.sprite_sheet, seq_rows, seq_cols)
        for i in range(seq_rows):
            self._animations.append(image.Animation.from_image_sequence(
                seq[i * seq_cols:(i + 1) * seq_cols], (1 / TICKS_PER_SEC) * TICKS_PER_FRAME, True))
