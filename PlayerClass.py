from Constants import *
import pygame

from GameObject import GameObject


class Player(GameObject):
    def __init__(self, game_object, x, y, w, h):
        GameObject.__init__(self, game_object, x, y, w, h)

        self.direction = DOWN
        self.animationState = ANIM_DOWNIDLE
        self.frameCount = 0 #no. of frames since game started
        self.currentFrame = 0
        self.maxFrames = 2
        self.frameRect = pygame.Rect(self.currentFrame * SPRITE_WIDTH, self.animationState * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT)

        self.spriteSheet = pygame.image.load('characters/GhostSheet.png').convert()
        self.spriteSheet.set_colorkey((255,0,255))


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

        # actually move
        self.move()