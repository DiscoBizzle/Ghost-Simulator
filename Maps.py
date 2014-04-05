import pygame
import Graphics
import json
from Constants import *


def test():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800))
    m = Map('tiles/martin.png', 'tiles/martin.json')

    surf = Graphics.draw_map(m)

    screen.blit(surf, (0, 0))

    pygame.display.update()
    raw_input()
    pygame.quit()


def load_map(map_filename): # Load a map from a map file

    #map_f = open(map_filename, 'r')
    data = json.load(open(map_filename))

    width = data['tileswide']
    height = data['tileshigh']

    
    tile_map = data['layers'][0]['tiles']

    grid = [[0 for i in range(width)] for j in range(height)]
        
    for tile in tile_map:
        x = tile['x']
        y = tile['y']
        grid[y][x] = tile['tile']

    #print grid

    return grid


class Tile(object):
    def __init__(self, tile_ref, map, pos):
        if tile_ref != -1:
            self.tileset_coord = (tile_ref % map.tileset_cols, tile_ref / map.tileset_cols)
        else:
            self.tileset_coord = (0, 0)

        self.tileset_area = (self.tileset_coord[0] * TILE_SIZE, self.tileset_coord[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.walkable = True
        self.tile_ref = tile_ref
        self.rect = pygame.Rect((pos[0] * TILE_SIZE, pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        if self.tile_ref in map.unwalkable:
            self.walkable = False


class Map(object):
    def __init__(self, tileset, map_file):
        self.tileset = pygame.image.load(tileset).convert()
        self.unwalkable = [211, 212, 227, 228, 259, 260, 292]
        self.tileset_cols = self.tileset.get_width() / TILE_SIZE

        tile_type_grid = load_map(map_file)

        self.grid = [[Tile(tile_type_grid[i][j], self, (i, j)) for i in range(len(tile_type_grid))] for j in range(len(tile_type_grid[0]))]


# test()
