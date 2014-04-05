from Constants import *


def check_screen_collision(p):
    pro_pos = (p.coord[0] + p.velocity[0], p.coord[1] + p.velocity[1])
    if pro_pos[0] > 0 and pro_pos[0] + p.dimensions[0] < WINDOW_WIDTH and \
       pro_pos[1] > 0 and pro_pos[1] + p.dimensions[1] < WINDOW_HEIGHT:
        return pro_pos
    elif p.velocity[0] < 0 and pro_pos[0] > 0:
        return (0, pro_pos[1])
    elif p.velocity[1] < 0 and pro_pos[1] > 0:
        return (pro_pos[0], 0)
    elif p.velocity[0] > 0 and pro_pos[0] < WINDOW_WIDTH:
        return (WINDOW_WIDTH, pro_pos[1])
    elif p.velocity[1] > 0 and pro_pos[1] < WINDOW_HEIGHT:
        return (pro_pos[0], WINDOW_HEIGHT)

    return p.coord



class Player:
    def __init__(self,x,y,w,h):
        self.coord = (x,y)  # top left
        self.dimensions = (w,h)
        self.velocity = (0,0)

    def update(self):
        self.coord = check_screen_collision(self)