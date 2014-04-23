import json
import os.path

import pygame
import pyglet
import pyglet.gl

from gslib import graphics
from gslib import character
from gslib import triggers
from gslib import character_objects
from gslib import character_functions
# from gslib import save_load
from gslib.constants import *

class FakeGame(object):
    def __init__(self, mmap):
        self.dimensions = (800, 600)
        self.world_objects_to_draw = []
        self.map = mmap

def test():
    m = Map(os.path.join(TILES_DIR, 'level2.png'), os.path.join(TILES_DIR, 'level2.json'), None)
    g = graphics.Graphics(FakeGame(m))

    surf = g.draw_map()

    window = pyglet.window.Window()


    @window.event
    def on_draw():
        print('surf len: ' + str(len(surf)))
        for spr in surf:
            spr.draw()
        #for i in range(10):
            #surf[i].draw()

    #pygame.display.update()
    pyglet.app.run()
    raw_input()

def open_map_json(map_filename):
    try:
        f = open(map_filename, 'r')
        data = json.load(f)
        f.close()
    except IOError:
        print("Couldn't open map file \"" + map_filename + "\".")

    return data

def load_map(map_filename): # Load a map and objects from a map file
    data = open_map_json(map_filename)

    width = data['tileswide']
    height = data['tileshigh']

    # Use the last "tiles" layer to get the tile map -- in the future will need to get more layers
    all_layers = [item for item in data['layers'] if "tiles" in item]

    for l in all_layers:
        if l['name'] == 'background':
            tile_map = l['tiles']
        elif l['name'] == 'collision':
            coll_map = l['tiles']

    map_grid = [[0 for i in range(height)] for j in range(width)]
    coll_grid = [[0 for i in range(height)] for j in range(width)]

    for tile in tile_map:
        x = tile['x']
        y = height - tile['y'] - 1
        map_grid[x][y] = tile['tile']

    for tile in coll_map:
        x = tile['x']
        y = height - tile['y'] - 1
        coll_grid[x][y] = tile['tile']

    return map_grid, coll_grid


def load_objects(map_filename):
    data = open_map_json(map_filename)
    try:
        obj_list = data['layers'][1]['objects']
    except:
        obj_list = []
        print("Couldn't load any objects from map file \"" + map_filename + "\".")
    return obj_list


class Tile(object):
    def __init__(self, tile_type_grid, coll_grid, m, pos):
        x, y = pos
        tile_ref = tile_type_grid[x][y]
        if tile_ref != -1:
            self.tileset_coord = ((m.tileset_rows - 1) - tile_ref // m.tileset_cols,
                                  tile_ref % m.tileset_cols)
        else:
            self.tileset_coord = (m.tileset_rows - 1, 0)

        self.walkable = True
        self.tile_ref = tile_ref
        self.rect = pygame.Rect((x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        if coll_grid:
            if coll_grid[x][y] == 1330:
                self.walkable = False
        else:
            if self.tile_ref in m.unwalkable:
                self.walkable = False


class Map(object):
    def __init__(self, name, tileset, map_file, game_class):
        self._name = name
        self._tileset_file = tileset
        self._map_file = map_file
        # Note: We need the PIL decoder for this to be anything like fast. (GDI+ etc import bitmaps upside-down...)
        self.tileset = pyglet.image.load(tileset).get_texture().get_image_data()
        self.tileset_cols = self.tileset.width // TILE_SIZE
        self.tileset_rows = self.tileset.height // TILE_SIZE

        self.tileset_seq = pyglet.image.ImageGrid(self.tileset, self.tileset_rows, self.tileset_cols)

        tile_type_grid, coll_grid = load_map(map_file)
        self.grid = [[Tile(tile_type_grid, coll_grid, self, (i, j)) for j in range(len(tile_type_grid[0]))] for i in range(len(tile_type_grid))]

        self.objects = {}

        self.triggers = {}

    def create_object_from_dict(self, d, game_class):
        if d['object_type'] == "character":
            try:
                self.objects[d['reference']] = character.Character(game_class, d['x'], d['y'], d['sprite_w'], d['sprite_h'], character.gen_character(), sprite_sheet=d['sprite_sheet'])
            except:
                print("Couldn't create an object from map file")



if __name__ == '__main__':
    test()
