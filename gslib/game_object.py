import time

import pygame

from gslib.constants import *

from gslib import fear_functions

class GameObject(object):
    def __init__(self, game_class, x, y, w, h, sprite_sheet):
        """
        To add an object to a map:
        map.objects.append(object)

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


        self.states = {}
        self.states['state1'] = {'max_speed': 1, 'fear_radius': 50}
        self.states['state2'] = {'max_speed': 5, 'fear_radius': 150}
        self._state_index = 'state1'

        self._coord = (x, y)  # top left
        self._dimensions = (w, h)
        self.velocity = (0, 0)
        self.min_speed = 0
        self.current_speed = 1
        self.normal_speed = 2
        self.fear_speed = 0
        self.fear_radius = 50
        self.scared_of = []
        self.fears = []
        self.rect = pygame.Rect(self.coord, self.dimensions)
        self.update_timer = 40
        self.fear_timer = 0
        self.scream_timer = 0
        self.fear = 0
        self.scream_thresh = 50

        #variables for animation
        self.sprite_sheet = sprite_sheet
        self._animation_state = ANIM_DOWNIDLE
        self.frame_count = 0
        self._current_frame = 0
        self.max_frames = 3
        self.sprite_width = SPRITE_WIDTH
        self.sprite_height = SPRITE_HEIGHT
        self.frame_rect = pygame.Rect(self.current_frame * self.sprite_width, self.animation_state * self.sprite_height,
                                      self.sprite_width, self.sprite_height)
        self.sprite_sheet.set_colorkey((255, 0, 255))

        #trigger functions
        self.has_touched_function = None
        self.is_touched_function = None

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.highlight_radius = 20

        self.possessed_by = None

        self.flair = {}
        self.collision_weight = 1  # set to 0 for no collision, can only push things that are lighter, or same weight

    def get_state_index(self):
        return self._state_index
    def set_state_index(self, index):
        self._state_index = index
        for k, v in self.states[index].iteritems():
            setattr(self, k, v)
    state_index = property(get_state_index, set_state_index)

    def get_coord(self):
        return self._coord
    def set_coord(self, new):
        self._coord = new
        self.rect = pygame.Rect(self._coord, self._dimensions)
    coord = property(get_coord, set_coord)

    def get_dimensions(self):
        return self._dimensions
    def set_dimensions(self, new):
        self._dimensions = new
        self.rect = pygame.Rect(self._coord, self._dimensions)
    dimensions = property(get_dimensions, set_dimensions)

    def get_current_frame(self):
        return self._current_frame
    def set_current_frame(self, val):
        self._current_frame = val
        self.frame_rect = pygame.Rect(self._current_frame * self.sprite_width, self._animation_state * self.sprite_height,
                                      self.sprite_width, self.sprite_height)
    current_frame = property(get_current_frame, set_current_frame)

    def get_animation_state(self):
        return self._animation_state
    def set_animation_state(self, val):
        self._animation_state = val
        self.frame_rect = pygame.Rect(self._current_frame * self.sprite_width, self._animation_state * self.sprite_height,
                                      self.sprite_width, self.sprite_height)
    animation_state = property(get_animation_state, set_animation_state)

    def update(self):
        v_x, v_y = 0, 0
        if self.move_down:
            v_y += self.current_speed
            self.direction = DOWN
        if self.move_up:
            v_y -= self.current_speed
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
        self.apply_fear()
        self.animate()

    def check_distance(self, other, distance):  # centre to centre distance is checked
        if self.get_distance_squared(other) < distance**2:
            return True
        else:
            return False

    def get_distance_squared(self, other):
        x = self.coord[0] + self.dimensions[0]/2 - (other.coord[0] + other.dimensions[0]/2)
        y = self.coord[1] + self.dimensions[1]/2 - (other.coord[1] + other.dimensions[1]/2)
        return x**2 + y**2

    def apply_fear(self):
        for o in self.game_class.objects:
            if hasattr(o, 'possessing'):  # checks if object is a player as can't import player module
                if o.possessing:
                    continue
            else:
                o.get_feared_by(self)

                if o.fear >= o.scream_thresh:
                    if o.scream_timer <= 0:
                        self.game_class.sound_dict['scream'].play()
                        o.scream_timer = 120
                    else:
                        o.scream_timer -= 1

    def get_feared_by(self, other):
        fear_level = 0
        if self.check_distance(other, self.fear_radius):
            for fear in other.fears:
                if fear in self.scared_of:
                    fear_level += 50
                    self.fear_timer = 5
                    self.feared_by_obj = other
                    self.feared_from_pos = other.coord

        self.fear = fear_level

    def move(self):
        x_ticks, y_ticks = abs(self.velocity[0]), abs(self.velocity[1])
        move_x_per_tick, move_y_per_tick = 1 if self.velocity[0] > 0 else -1, 1 if self.velocity[1] > 0 else -1

        while x_ticks > 0 or y_ticks > 0:
            if x_ticks > 0:
                self.movePx(move_x_per_tick, 0)
                x_ticks -= 1
            if y_ticks > 0:
                self.movePx(0, move_y_per_tick)
                y_ticks -= 1

    def movePx(self, x_dir, y_dir):
        # print '\n'
        collision = False

        # collide againt map boundaries
        pro_pos = (self.coord[0] + x_dir, self.coord[1] + y_dir)
        pro_rect = pygame.Rect(pro_pos, self.dimensions)
        if pro_pos[0] >= 0 and pro_pos[0] + self.dimensions[0] <= LEVEL_WIDTH and \
                        pro_pos[1] >= 0 and pro_pos[1] + self.dimensions[1] <= LEVEL_HEIGHT:
            pass
        else:
            collision = True

        # collision detection against map tiles
        # NOTE: assumes largest object w/ collision is 64x64 (i.e. 2x2 tiles)

        if pro_pos[0] >= 0 and pro_pos[1] >= 0:
            i = pro_pos[0] / TILE_SIZE  # get the index of the upper left tile
            j = pro_pos[1] / TILE_SIZE
        else:
            i = 0
            j = 0

        #check collision against the 9 possible tiles surrounding object
        for ni in range(i, i + 2):
            for nj in range(j, j + 2):
                if ni >= 0 and ni < LEVEL_WIDTH / TILE_SIZE and nj >= 0 and nj < LEVEL_HEIGHT / TILE_SIZE:
                    if not self.game_class.map.grid[ni][nj].walkable:
                        # pygame.draw.rect(self.game_class.surface, (200, 0, 0), self.rect)
                        # pygame.draw.rect(self.game_class.surface, (0, 200, 0), self.game_class.map.grid[ni][nj].rect)
                        # pygame.display.update()
                        # time.sleep(0.1)
                        if pro_rect.colliderect(self.game_class.map.grid[ni][nj].rect):
                            collision = True
                            # print('collision!')

        # collision against other objects
        for o in self.game_class.objects:
            if not o is self:
                if o.collision_weight and self.collision_weight:  # check if obj collides at all
                    if pro_rect.colliderect(o.rect):
                        if o.is_touched_function:
                            o.is_touched_function()
                        if self.has_touched_function:
                            self.has_touched_function()

                        if self.collision_weight < o.collision_weight:  # check if obj can be pushed by self
                            collision = True
                        else:  # push object
                            temp = o.collision_weight
                            o.collision_weight = self.collision_weight - o.collision_weight  # allows to push chain of objs
                            collision = o.movePx(x_dir, y_dir)  # collsion of self is dependent on whether obj collided
                            o.collision_weight = temp

        if not collision:
            self.coord = pro_pos
        return collision

    def animate(self):
        self.frame_count += 1
        if (self.frame_count % TICKS_PER_FRAME) == 0:
            self.current_frame += 1

        if self.current_frame > self.max_frames:
            self.current_frame = 0

        if self.velocity[1] == 0 and self.velocity[0] == 0:
            if self.animation_state == ANIM_DOWNWALK:
                self.animation_state = ANIM_DOWNIDLE
            if self.animation_state == ANIM_RIGHTWALK:
                self.animation_state = ANIM_RIGHTIDLE
            if self.animation_state == ANIM_UPWALK:
                self.animation_state = ANIM_UPIDLE
            if self.animation_state == ANIM_LEFTWALK:
                self.animation_state = ANIM_LEFTIDLE
        else:
            if self.velocity[1] > 0:
                self.animation_state = ANIM_DOWNWALK
            elif self.velocity[1] < 0:
                self.animation_state = ANIM_UPWALK

            if self.velocity[0] > 0:
                self.animation_state = ANIM_RIGHTWALK
            elif self.velocity[0] < 0:
                self.animation_state = ANIM_LEFTWALK

        # self.frame_rect = pygame.Rect(self.current_frame * SPRITE_WIDTH, self.animation_state * SPRITE_HEIGHT,
        #                               SPRITE_WIDTH, SPRITE_HEIGHT)

