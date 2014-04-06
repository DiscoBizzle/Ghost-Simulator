import json
import os.path

import pygame

from gslib import graphics
from gslib import character
from gslib.constants import *

def test():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800))
    m = Map(os.path.join(TILE_DIR, 'martin.png'), os.path.join(TILE_DIR, 'martin.json'))

    surf = graphics.draw_map(m)

    screen.blit(surf, (0, 0))

    pygame.display.update()
    raw_input()
    pygame.quit()

def open_map_json(map_filename):
    try:
        f = open(map_filename, 'r')
        data = json.load(f)
        f.close()
    except IOError:
        print "Couldn't open map file \"" + map_filename + "\"."

    return data

def load_map(map_filename): # Load a map and objects from a map file
    data = open_map_json(map_filename)

    width = data['tileswide']
    height = data['tileshigh']

    
    tile_map = data['layers'][0]['tiles']
    map_grid = [[0 for i in range(height)] for j in range(width)]
        
    for tile in tile_map:
        x = tile['x']
        y = tile['y']
        map_grid[x][y] = tile['tile']


    return map_grid

def load_objects(map_filename):
    data = open_map_json(map_filename)
    try:
        obj_list = data['layers'][1]['objects']
    except:
        obj_list = []
        print "Couldn't load any objects from map file \"" + map_filename + "\"."
    return obj_list

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
    def __init__(self, tileset, map_file, game_class):
        self.tileset = pygame.image.load(tileset).convert()
        self.unwalkable = [211, 212, 227, 228, 259, 260, 275, 276, 292, 491, 493, 501, 502, 517, 518, 583, 584, 599,
                           600, 615, 616, 631, 632, 1046, 1236, 1252, 1302, 1303, 1304, 1318, 1319, 1320,
                           995, 915, 916, 931, 932, 1081, 1082, 1083, 1097, 1099, 346, 1032, 196, 244,
                           ]
        self.tileset_cols = self.tileset.get_width() / TILE_SIZE

        tile_type_grid = load_map(map_file)
        self.grid = [[Tile(tile_type_grid[i][j], self, (i, j)) for j in range(len(tile_type_grid[0]))] for i in range(len(tile_type_grid))]

        loaded_objects = load_objects(map_file) # gives a list of dicts, each dict associated with an object from the map
        
        self.objects = []

        for i in range(2):
            self.objects.append(character.Character(game_class, 0, 0, 16, 16, character.gen_character()))

        for o_dict in loaded_objects:
            if o_dict['object_type']=="hat":
                self.objects.append(character.Character(game_class, o_dict['x'], o_dict['y'], 16, 16, character.gen_character()))



if __name__ == '__main__':
    test()
