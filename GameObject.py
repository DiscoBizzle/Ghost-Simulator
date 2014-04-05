from Constants import *


class GameObject:
    def __init__(self, game_class, x, y, w, h):
        self.game_class = game_class

        self.coord = (x,y)  # top left
        self.dimensions = (w,h)
        self.velocity = (0,0)
        self.attributes = []

    def move(self):
        pro_pos = (self.coord[0] + self.velocity[0], self.coord[1] + self.velocity[1])
        if pro_pos[0] >= 0 and pro_pos[0] + self.dimensions[0] <= LEVEL_WIDTH and \
                pro_pos[1] >= 0 and pro_pos[1] + self.dimensions[1] <= LEVEL_HEIGHT:
            self.coord = pro_pos
    
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