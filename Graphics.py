import pygame
# import Maps
from Constants import *

# screen = pygame.display.set_mode((800, 800))

def draw_map(m):
    grid_size = TILE_SIZE
    nw = len(m.grid)
    nh = len(m.grid[0])
    surf = pygame.Surface((nw * grid_size, nh * grid_size))

    for i in range(nw):
        for j in range(nh):
            area = m.grid[i][j].tileset_area
            surf.blit(m.tileset, (i * grid_size, j * grid_size), area)

    return surf
