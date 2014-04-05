from Constants import *
import pygame


class GameObject:
    def __init__(self, game_class, x, y, w, h):
        self.game_class = game_class

        self.coord = (x,y)  # top left
        self.dimensions = (w,h)
        self.velocity = (0,0)
        self.attributes = []
        self.sprite = None
        self.frameRect = None
        self.rect = pygame.Rect(self.coord, self.dimensions)
        self.update_timer = 0


    def update(self):
        self.move()
        self.rect = pygame.Rect(self.coord, self.dimensions)

    def move(self):
        pro_pos = (self.coord[0] + self.velocity[0], self.coord[1] + self.velocity[1])
        if pro_pos[0] >= 0 and pro_pos[0] + self.dimensions[0] <= LEVEL_WIDTH and \
                pro_pos[1] >= 0 and pro_pos[1] + self.dimensions[1] <= LEVEL_HEIGHT:
            self.coord = pro_pos

        # begin collision detection NOTE: assumes largest object w/ collision is 64x64 (i.e. 2x2 tiles)
        i = pro_pos[0]/self.dimensions[0]  # get the index of the upper right tile
        j = pro_pos[1]/self.dimensions[1]

        #check collision against the 9 possible
        for ni in range(i,i+2):
            for nj in range(j, j+2):
                pass

        #end collision detection

        x, y = pro_pos
    
        if self.velocity[0] < 0:
            if self.coord[0] + self.velocity[0] <= 0:
                x = 0
        elif self.velocity[0] > 0:
            if self.coord[0] + self.dimensions[0] + self.velocity[0] >= LEVEL_WIDTH:
                x = LEVEL_WIDTH - self.dimensions[0]
        if self.velocity[1] < 0:
            if self.coord[1] + self.velocity[1] <= 0:
                y = 0
        elif self.velocity[1] > 0:
            if self.coord[1] + self.dimensions[1] + self.velocity[1] >= LEVEL_HEIGHT:
                y = LEVEL_HEIGHT - self.dimensions[1]

        self.coord = x, y