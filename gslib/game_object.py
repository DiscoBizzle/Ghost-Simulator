import pygame
import time

from gslib.constants import *

class GameObject(object):
    def __init__(self, game_class, x, y, w, h):
        self.game_class = game_class

        self.coord = (x,y)  # top left
        self.dimensions = (w,h)
        self.velocity = (0,0)
        self.max_velocity = 1
        self.fear_radius = 50
        self.feared_by = []
        self.fears = []
        self.sprite = None
        self.frameRect = None
        self.rect = pygame.Rect(self.coord, self.dimensions)
        self.update_timer = 0
        self.fear_timer = 0

    def update(self):
        if not self.velocity == (0, 0):
            self.move()
        self.rect = pygame.Rect(self.coord, self.dimensions)
        self.apply_fear()

    def apply_fear(self):
        for o in self.game_class.objects:
            if o is not self:
                for f in self.fears:
                    if f in o.feared_by:
                        if (o.coord[0] - self.coord[0])**2 + (o.coord[1] - self.coord[1])**2 < self.fear_radius**2:
                            o.fear_timer = 5
                            self.game_class.player1.fear += 100


    def move(self):
        # print '\n'
        collision = False

        pro_pos = (self.coord[0] + self.velocity[0], self.coord[1] + self.velocity[1])
        pro_rect = pygame.Rect(pro_pos, self.dimensions)
        if pro_pos[0] >= 0 and pro_pos[0] + self.dimensions[0] <= LEVEL_WIDTH and \
                pro_pos[1] >= 0 and pro_pos[1] + self.dimensions[1] <= LEVEL_HEIGHT:
            self.coord = pro_pos
        else:
            collision = True

        # begin collision detection NOTE: assumes largest object w/ collision is 64x64 (i.e. 2x2 tiles)

        if pro_pos[0] > 0 and pro_pos[1] > 0:
            i = pro_pos[0]/TILE_SIZE  # get the index of the upper right tile
            j = pro_pos[1]/TILE_SIZE
        else:
            i = 0
            j = 0

        #check collision against the 9 possible tiles surrounding object
        for ni in range(i, i+2):
            for nj in range(j, j+2):
                if ni > 0 and ni < LEVEL_WIDTH/TILE_SIZE and nj > 0 and nj < LEVEL_HEIGHT/TILE_SIZE:
                    if not self.game_class.map.grid[ni][nj].walkable:
                        # pygame.draw.rect(self.game_class.surface, (200, 0, 0), self.rect)
                        # pygame.draw.rect(self.game_class.surface, (0, 200, 0), self.game_class.map.grid[ni][nj].rect)
                        # pygame.display.update()
                        # time.sleep(0.1)
                        if pro_rect.colliderect(self.game_class.map.grid[ni][nj].rect):
                            collision = True
                            # print('collision!')

        #end collision detection

        #handle collision
        if not collision: # if no collision is detected, carry update position immediately
            self.coord = pro_pos
            return
        else: # if collision, deal with it, beeatch
            x, y = pro_pos

            #collision with level boundaries
            if self.velocity[0] < 0:
                if x <= 0:
                    x = 0
            elif self.velocity[0] > 0:
                if x + self.dimensions[0] >= LEVEL_WIDTH:
                    x = LEVEL_WIDTH - self.dimensions[0]
            if self.velocity[1] < 0:
                if y <= 0:
                    y = 0
            elif self.velocity[1] > 0:
                if y + self.dimensions[1] >= LEVEL_HEIGHT:
                    y = LEVEL_HEIGHT - self.dimensions[1]

            #collision with tiles

            if self.velocity[0] < 0: #if moving left, check collision with leftmost 3 tiles, push out if collision
                for nj in range (j, j+2):
                    if nj > 0 and nj < LEVEL_HEIGHT/TILE_SIZE:
                        if not self.game_class.map.grid[i][nj].walkable:
                            if pro_rect.colliderect(self.game_class.map.grid[i][nj].rect):
                               x = self.game_class.map.grid[i][nj].rect.x + TILE_SIZE

            elif self.velocity[0] > 0: #same for rightmost tiles
                li = (self.coord[0] + self.dimensions[0])/TILE_SIZE
                for nj in range (j, j+2):
                    if nj > 0 and nj < LEVEL_HEIGHT/TILE_SIZE and li > 0 and li < LEVEL_WIDTH/TILE_SIZE:
                        if not self.game_class.map.grid[li][nj].walkable:
                            if pro_rect.colliderect(self.game_class.map.grid[li][nj].rect):
                               x = self.game_class.map.grid[li][nj].rect.x - self.dimensions[0]

            if self.velocity[1] < 0: #if moving up, check collision with uppermost 3 tiles, push out if collision
                for ni in range (i, i+2):
                    if ni > 0 and ni < LEVEL_WIDTH/TILE_SIZE:
                        if not self.game_class.map.grid[ni][j].walkable:
                            if pro_rect.colliderect(self.game_class.map.grid[ni][j].rect):
                               y = self.game_class.map.grid[ni][j].rect.y + TILE_SIZE

            elif self.velocity[1] > 0: #same for rightmost tiles
                lj = (self.coord[1] + self.dimensions[1])/TILE_SIZE
                for ni in range (i, i+2):
                    if ni > 0 and ni < LEVEL_WIDTH/TILE_SIZE and lj > 0 and lj < LEVEL_HEIGHT/TILE_SIZE:
                        if not self.game_class.map.grid[ni][lj].walkable:
                            if pro_rect.colliderect(self.game_class.map.grid[ni][lj].rect):
                               y = self.game_class.map.grid[ni][lj].rect.y - self.dimensions[1]



        self.coord = x, y