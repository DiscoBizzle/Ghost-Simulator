import pygame

from gslib.constants import *
from gslib.game_object import GameObject


class Player(GameObject):
    def __init__(self, game_class, x, y, w, h):
        sprite_sheet = pygame.image.load('characters/GhostSheet.png').convert()
        GameObject.__init__(self, game_class, x, y, w, h, sprite_sheet)

        self.direction = DOWN
        self.animationState = ANIM_DOWNIDLE
        self.frameCount = 0 #no. of frames since game started
        self.currentFrame = 0
        self.maxFrames = 3
        self.frameRect = pygame.Rect(self.currentFrame * SPRITE_WIDTH, self.animationState * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT)

        self._fear = START_FEAR
        self.fears = ['player']
        self.skills_learnt = []

    def get_fear(self):
        return self._fear
    def set_fear(self, f):
        self._fear = f
        if self._fear > MAX_FEAR:
            self._fear = MAX_FEAR
    fear = property(get_fear, set_fear)

    def learn_skill(self, skill):
        if skill.can_be_learnt(self):
            self.skills_learnt.append(skill.name)
            for effect in skill.effects:
                #apply effect
                pass



    def update(self):
        # update velocity
        v_x, v_y = 0, 0

        self.animationState = self.direction

        if self.game_class.keys[pygame.K_DOWN]:
            v_y += 5
            self.direction = DOWN
            self.animationState = ANIM_DOWNWALK
        if self.game_class.keys[pygame.K_UP]:
            v_y -= 5
            self.direction = UP
            self.animationState = ANIM_UPWALK
        if self.game_class.keys[pygame.K_LEFT]:
            v_x -= 5
            self.direction = LEFT
            self.animationState = ANIM_LEFTWALK
        if self.game_class.keys[pygame.K_RIGHT]:
            v_x += 5
            self.direction = RIGHT
            self.animationState = ANIM_RIGHTWALK

        self.frameCount += 1
        if (self.frameCount % 4) == 0:
            self.currentFrame += 1

        if self.currentFrame > self.maxFrames:
            self.currentFrame = 0

        self.frameRect = pygame.Rect(self.currentFrame * SPRITE_WIDTH, self.animationState * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT)

        self.velocity = (v_x, v_y)

        if v_x != 0 or v_y != 0:
            self.fear -= FEAR_PER_STEP * (v_x*v_x + v_y*v_y)**.5
        else:
            self.fear -= FEAR_PER_TICK

        if self.fear <= 0:
            self.game_class.GameState = GAME_OVER
            self.fear = START_FEAR

        # move etc.
        GameObject.update(self)
