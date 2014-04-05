import pygame
import Graphics
import json
from Constants import *


def test():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800))
    m = Map('tileset_test.png', 'tiles/testa.json', [[Tile(i*j) for i in range(10)] for j in range(10)])

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
        grid[x][y] = tile['tile']

    #print grid

    return grid

class Tile(object):
    def __init__(self, coord):
        self.tileset_coord = (coord, 0)
        self.tileset_tile_size = TILE_SIZE
        self.tileset_area = (self.tileset_coord[0] * self.tileset_tile_size, self.tileset_coord[1] * self.tileset_tile_size, self.tileset_tile_size, self.tileset_tile_size)
        self.walkable = True


class Map(object):
    def __init__(self, tileset, map_file, grid):
        self.tileset = pygame.image.load(tileset).convert()
        self.grid = grid



test()
