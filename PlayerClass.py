from Constants import *


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

    def update(self):
        if check_screen_collision(self):
            self.coord = (self.coord[0] + self.velocity[0], self.coord[1] + self.velocity[1])