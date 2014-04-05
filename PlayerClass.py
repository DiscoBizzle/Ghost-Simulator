class Player:
    def __init__(self,x,y,w,h):
        self.coord = (x,y)
        self.dimensions = (w,h)
        self.velocity = (0,0)

    def update(self):
        self.coord = (self.coord[0] + self.velocity[0], self.coord[1] + self.velocity[1])