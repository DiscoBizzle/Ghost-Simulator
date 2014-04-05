from Constants import *
import pygame


def check_screen_collision(p):
    pro_pos = (p.coord[0] + p.velocity[0], p.coord[1] + p.velocity[1])
    if pro_pos[0] >= 0 and pro_pos[0] + p.dimensions[0] <= LEVEL_WIDTH and \
       pro_pos[1] >= 0 and pro_pos[1] + p.dimensions[1] <= LEVEL_HEIGHT:
        return pro_pos

    x, y = pro_pos

    if p.velocity[0] < 0:
        if p.coord[0] + p.velocity[0] <= 0:
            x = 0
    elif p.velocity[0] > 0:
        if p.coord[0] + p.dimensions[0] + p.velocity[0] >= LEVEL_WIDTH:
            x = LEVEL_WIDTH - p.dimensions[0]
    if p.velocity[1] < 0:
        if p.coord[1] + p.velocity[1] <= 0:
            y = 0
    elif p.velocity[1] > 0:
        if p.coord[1] + p.dimensions[1] + p.velocity[1] >= LEVEL_HEIGHT:
            y = LEVEL_HEIGHT - p.dimensions[1]

    return x, y


class Player:
    def __init__(self,x,y,w,h):
        self.coord = (x,y)  # top left
        self.dimensions = (w,h)
        self.velocity = (0,0)

    def update(self, gameClass):
        # update velocity
        v_x, v_y = 0, 0
        if gameClass.keys[pygame.K_DOWN]:
            v_y += 5
        if gameClass.keys[pygame.K_UP]:
            v_y -= 5
        if gameClass.keys[pygame.K_LEFT]:
            v_x -= 5
        if gameClass.keys[pygame.K_RIGHT]:
            v_x += 5

        self.velocity = (v_x, v_y)

        # actually move
        self.coord = check_screen_collision(self)