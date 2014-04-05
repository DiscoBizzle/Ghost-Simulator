import GameClass
import pygame

screen = pygame.display.set_mode((800, 800))

def test():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800))

    tileset = Tileset('tileset_test.png')
    background = [[0, 1, 2],
                  [1, 2, 0],
                  [2, 1, 0],
                  [1, 2, 0],
                  ]

    surf = draw_grid(background, tileset)

    screen.blit(surf, (0, 0))

    pygame.display.update()
    raw_input()
    pygame.quit()


class Tileset(object):
    def __init__(self, file):
        self.tileset = pygame.image.load(file).convert()
        self.tile_size = 40  # tile size in file

    def get_sprite(self, ref):
        coord = (0, 0)
        if ref == 1:
            coord = (1, 0)
        elif ref == 2:
            coord = (2, 0)

        area = (coord[0] * self.tile_size, coord[1] * self.tile_size, self.tile_size, self.tile_size)
        return area


def draw_grid(grid, tileset):
    grid_size = 20
    nw = len(grid)
    nh = len(grid[0])
    surf = pygame.Surface((nw * grid_size, nh * grid_size))

    for i in range(nw):
        for j in range(nh):
            area = tileset.get_sprite(grid[i][j])
            surf.blit(tileset.tileset, (i * grid_size, j * grid_size), area)

    return surf


test()