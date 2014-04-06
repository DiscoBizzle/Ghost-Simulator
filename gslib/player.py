import pygame

from gslib.constants import *
from gslib.game_object import GameObject


class Player(GameObject):
    def __init__(self, game_class, x, y, w, h):
        sprite_sheet = pygame.image.load('characters/GhostSheet.png').convert()
        GameObject.__init__(self, game_class, x, y, w, h, sprite_sheet)

        self.direction = DOWN
        self.animation_state = ANIM_DOWNIDLE
        self.frame_rect = pygame.Rect(self.current_frame * SPRITE_WIDTH, self.animation_state * SPRITE_HEIGHT,
                                      SPRITE_WIDTH, SPRITE_HEIGHT)

        self._fear = START_FEAR
        self.fears = ['player']
        self.skills_learnt = []

        self.possessing = False

    def get_fear(self):
        return self._fear

    def set_fear(self, f):
        self._fear = f
        if self._fear > MAX_FEAR:
            self._fear = MAX_FEAR

    fear = property(get_fear, set_fear)

    def learn_skill(self, skill):
        if self.game_class.skills_dict[skill].can_be_learnt(self):
            self.skills_learnt.append(self.game_class.skills_dict[skill].name)
            for effect in self.game_class.skills_dict[skill].effects:
                #apply effect
                pass
            return True
        return False


    def update(self):
        # update velocity
        v_x, v_y = 0, 0

        self.animation_state = self.direction

        if self.game_class.keys[pygame.K_DOWN]:
            v_y += 5
            self.direction = DOWN
            self.animation_state = ANIM_DOWNWALK
        if self.game_class.keys[pygame.K_UP]:
            v_y -= 5
            self.direction = UP
            self.animation_state = ANIM_UPWALK
        if self.game_class.keys[pygame.K_LEFT]:
            v_x -= 5
            self.direction = LEFT
            self.animation_state = ANIM_LEFTWALK
        if self.game_class.keys[pygame.K_RIGHT]:
            v_x += 5
            self.direction = RIGHT
            self.animation_state = ANIM_RIGHTWALK

        self.frame_count += 1
        if (self.frame_count % 4) == 0:
            self.current_frame += 1

        if self.current_frame > self.max_frames:
            self.current_frame = 0

        self.frame_rect = pygame.Rect(self.current_frame * SPRITE_WIDTH, self.animation_state * SPRITE_HEIGHT,
                                      SPRITE_WIDTH, SPRITE_HEIGHT)

        self.velocity = (v_x, v_y)

        if v_x != 0 or v_y != 0:
            self.fear -= FEAR_PER_STEP * (v_x * v_x + v_y * v_y) ** .5
        else:
            self.fear -= FEAR_PER_TICK

        if self.fear <= 0:
            self.game_class.GameState = GAME_OVER
            self.fear = START_FEAR

        # move etc.
        GameObject.update(self)
