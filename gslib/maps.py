import itertools
import json
import os.path

import pyglet
import pyglet.gl

from gslib import graphics
from gslib import character
from gslib import rect
from gslib.constants import *


def open_map_json(map_filename):
    try:
        f = open(map_filename, 'r')
        data = json.load(f)
        f.close()
    except IOError:
        raise Exception("Couldn't open map file \"" + map_filename + "\".")

    return data


def _produce_collision(mid_layers, width, height):

    coll_grid = [[(False, None) for i in range(width)] for j in range(height)]

    for ml in mid_layers:
        for y in height:
            for x in width:
                if ml[y][x] != -1:
                    coll_grid[y][x] = (True, rect.Rect((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))

    return coll_grid


def load_map(map_filename): # Load a map and objects from a map file
    data = open_map_json(map_filename)

    width = data['tileswide']
    height = data['tileshigh']

    all_layers = [item for item in data['layers'] if "tiles" in item]

    tile_map = {}

    for l in all_layers:
        tile_map[l['name']] = l['tiles']

    map_grid = {}

    for k, m in tile_map.iteritems():
        tmp = [[0 for i in range(width)] for j in range(height)]
        for tile in m:
            x = tile['x']
            y = height - tile['y'] - 1
            tmp[y][x] = tile['tile']
        map_grid[k] = tmp

    mid_grid = []
    for k, g in map_grid.iteritems():
        if k.startswith("mid"):
            mid_grid.append(g)
    coll_grid = _produce_collision(mid_grid, width, height)

    return map_grid, coll_grid, width, height


class Tile(object):
    def __init__(self, tile_type_grid, coll_grid, m, pos):
        x, y = pos

        tile_ref = tile_type_grid[y][x]

        if tile_ref != -1:
            self.tileset_coord = ((m.tileset_rows - 1) - tile_ref // m.tileset_cols,
                                  tile_ref % m.tileset_cols)
        else:
            self.tileset_coord = (m.tileset_rows - 1, 0)

        self.tile_ref = tile_ref
        self.rect = rect.Rect((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE))

        if coll_grid and coll_grid[y][x]:
            self.walkable = False
        elif self.tile_ref == -1:
            self.walkable = False
        else:
            self.walkable = True


class Map(object):
    def __init__(self, name, tileset, map_file, cutscenes_file, game_class):
        self._name = name
        self._tileset_file = tileset
        self._map_file = map_file
        self._cutscenes_file = cutscenes_file

        # .get_texture().get_image_data() trick to ensure fast load
        self.tileset = pyglet.image.load(tileset).get_texture().get_image_data()
        self.tileset_cols = self.tileset.width // TILE_SIZE
        self.tileset_rows = self.tileset.height // TILE_SIZE

        self.tileset_seq = pyglet.image.ImageGrid(self.tileset, self.tileset_rows, self.tileset_cols)

        tile_type_grid, self.coll_grid, self.grid_width, self.grid_height = load_map(map_file)

        self.grid = {}

        for layer_name, layer in tile_type_grid.iteritems():
            self.grid[layer_name] = []

            for y in range(self.grid_height):
                self.grid[layer_name].append([])

                for x in range(self.grid_width):
                    print(len(layer), len(layer[0]))
                    self.grid[layer_name][y].append(Tile(layer, self.coll_grid, self, (x, y)))

        self.objects = {}

        self.cutscenes = {}
        self.active_cutscene = None

        self.triggers = {}
