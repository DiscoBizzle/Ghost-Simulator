import time

import pygame

from gslib.constants import *

from gslib import fear_functions

class GameObject(object):
    def __init__(self, game_class, x, y, w, h, sprite_sheet):
        self.game_class = game_class

        # each state has a name (consider using integers if you want to advance through them sequentially)
        # each state is a dict of properties that the object will update to when state_index is changed to that state name
        # ensure that these properties are spelt correctly!
        self.states = {}
        self.states['state1'] = {'max_speed': 1, 'fear_radius': 50}
        self.states['state2'] = {'max_speed': 5, 'fear_radius': 150}
        self._state_index = 'state1'

        self.coord = (x, y)  # top left
        self.dimensions = (w, h)
        self.velocity = (0, 0)
        self.current_speed = 1
        self.normal_speed = 2
        self.fear_speed = 10
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
        self.animation_state = ANIM_DOWNIDLE
        self.frame_count = 0
        self.current_frame = 0
        self.max_frames = 3
        self.frame_rect = pygame.Rect(self.current_frame * SPRITE_WIDTH, self.animation_state * SPRITE_HEIGHT,
                                      SPRITE_WIDTH, SPRITE_HEIGHT)
        self.sprite_sheet.set_colorkey((255, 0, 255))

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.highlight_radius = 20

        self.possessed_by = None

    def get_state_index(self):
        return self._state_index
    def set_state_index(self, index):
        self._state_index = index
        for k, v in self.states[index].iteritems():
            setattr(self, k, v)
    state_index = property(get_state_index, set_state_index)

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
        self.rect = pygame.Rect(self.coord, self.dimensions)
        self.apply_fear()
        self.animate()

    def check_distance(self, other, distance):  # centre to centre distance is checked
        x = self.coord[0] + self.dimensions[0]/2 - (other.coord[0] + other.dimensions[0]/2)
        y = self.coord[1] + self.dimensions[1]/2 - (other.coord[1] + other.dimensions[1]/2)
        if x**2 + y**2 < distance**2:
            return True
        else:
            return False


    def apply_fear(self):
        for o in self.game_class.objects:
            if hasattr(o, 'possessing'):
                if o.possessing:
                   continue
            if o is not self:
                for f in self.fears:
                    if f in o.scared_of:
                        old_fear_level = o.fear
                        o.fear = fear_functions.harvest_fear(self, o)
                        for p in self.game_class.players:
                            if o.check_distance(p, FEAR_COLLECTION_RADIUS):
                                p.fear += o.fear

                        if o.fear >= o.scream_thresh:
                            if o.scream_timer <= 0:
                                self.game_class.sound_dict['scream'].play()
                                o.scream_timer = 120
                            else:
                                o.scream_timer -= 1

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

        pro_pos = (self.coord[0] + x_dir, self.coord[1] + y_dir)
        pro_rect = pygame.Rect(pro_pos, self.dimensions)
        if pro_pos[0] >= 0 and pro_pos[0] + self.dimensions[0] <= LEVEL_WIDTH and \
                        pro_pos[1] >= 0 and pro_pos[1] + self.dimensions[1] <= LEVEL_HEIGHT:
            pass
        else:
            collision = True

        # begin collision detection NOTE: assumes largest object w/ collision is 64x64 (i.e. 2x2 tiles)

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

        if not collision:
            self.coord = pro_pos

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

        self.frame_rect = pygame.Rect(self.current_frame * SPRITE_WIDTH, self.animation_state * SPRITE_HEIGHT,
                                      SPRITE_WIDTH, SPRITE_HEIGHT)

