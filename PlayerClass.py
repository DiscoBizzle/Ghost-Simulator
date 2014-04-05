from Constants import *
import pygame

def check_screen_collision(p):
    if p.coord[0] > 0 and p.coord[0] + p.dimensions[0] < WINDOW_WIDTH and \
       p.coord[1] > 0 and p.coord[1] + p.dimensions[1] < WINDOW_HEIGHT:
        return True
    else:
        return False


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
        if check_screen_collision(self):
            self.coord = (self.coord[0] + self.velocity[0], self.coord[1] + self.velocity[1])