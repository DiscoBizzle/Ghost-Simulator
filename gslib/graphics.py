import pygame

# import Maps
from gslib.constants import *

# screen = pygame.display.set_mode((800, 800))
blue = pygame.Color(0,255,0)

def draw_map(m):
    grid_size = TILE_SIZE
    nw = len(m.grid)
    nh = len(m.grid[0])
    surf = pygame.Surface((nw * grid_size, nh * grid_size))

    for i in range(nw):
        for j in range(nh):
            area = m.grid[i][j].tileset_area
            surf.blit(m.tileset, (i * grid_size, j * grid_size), area)

            ##TEMPORARY - DRAWS SOLID TILES FOR COLLISION DEBUG
            if not m.grid[i][j].walkable:
                temprect = pygame.Rect(i * grid_size, j * grid_size, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surf, 0x0000ff, temprect)

    return surf
