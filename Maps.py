import pygame
import Graphics


def test():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800))
    m = Map('tileset_test.png')

    surf = Graphics.draw_map(m)

    screen.blit(surf, (0, 0))

    pygame.display.update()
    raw_input()
    pygame.quit()


class Tile(object):
    def __init__(self, n):
        self.tileset_coord = (n % 3, 0)
        self.tileset_tile_size = 40
        self.tileset_area = (self.tileset_coord[0] * self.tileset_tile_size, self.tileset_coord[1] * self.tileset_tile_size, self.tileset_tile_size, self.tileset_tile_size)
        self.walkable = True


class Map(object):
    def __init__(self, tileset):
        self.tileset = pygame.image.load(tileset).convert()
        self.tilseset_tile_size = 40  # tile size in file
        self.grid = [[Tile(i*j) for i in range(10)] for j in range(10)]


test()