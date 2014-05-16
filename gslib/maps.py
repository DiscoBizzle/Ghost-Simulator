from __future__ import absolute_import, division, print_function

import io
import json
import collections

import pyglet
import pyglet.gl
import pyglet.image

from gslib import rect
from gslib import static_object
from gslib.constants import *


def open_map_json(map_filename):
    try:
        with io.open(map_filename, 'rt', encoding='utf-8') as f:
            data = json.load(f)
    except IOError:
        raise Exception("Couldn't open map file \"" + map_filename + "\".")

    return data


def _get_mid_grids(all_grids):
    mid_grid = {}
    for k, g in all_grids.iteritems():
        if k.startswith("mid"):
            mid_grid[k] = g
    return mid_grid


def _produce_collision(mid_layers, width, height):

    coll_grid = [[(False, None) for i in range(width)] for j in range(height)]

    for ml_name, ml in mid_layers.iteritems():
        for y in range(height):
            for x in range(width):
                if ml[y][x] != -1:
                    coll_grid[y][x] = (True, rect.Rect((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))

    return coll_grid


def _render_static(r, tiles, tileset_seq, grid_width, grid_height):
    render_me = collections.OrderedDict()
    tex = pyglet.image.Texture.create(r.width, r.height)

    for x_s, y_s, d, t in tiles:
        x = x_s * TILE_SIZE - r.x
        y = y_s * TILE_SIZE - r.y
        t_c = ((tileset_seq.rows - 1) - t // tileset_seq.columns, t % tileset_seq.columns)

        if not d in render_me:
            render_me[d] = []

        render_me[d].append((x, y, t_c))

    for d, ts in render_me.iteritems():
        for x, y, t_c in ts:
            tex.blit_into(tileset_seq[t_c], x, y, 0)

    return tex


def _produce_statics_for_mid_grids(mid_grid, tileset_seq, grid_width, grid_height):
    # To get proper depth, we need to sort and render each full 'object' separately.
    # This function automatically produces objects, one for each set of horizontally touching tiles.

    # list of uneaten tiles
    uneaten = []
    for layer_name, layer_grid in mid_grid.iteritems():
        for y in range(grid_height):
            for x in range(grid_width):
                if layer_grid[y][x] != -1:
                    uneaten.append((x, y, int(layer_name[3:] or '0'), layer_grid[y][x]))

    # find groups of horizontally touching tiles
    touching = {}
    for x, y, d, t in uneaten:
        eaten = False
        r = rect.Rect((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE))

        for maybe_rect, maybe_friends in touching.iteritems():
            # horizontal touching!
            if rect.Rect(*maybe_rect).inflate(2, 0).colliderect(r):
                eaten = (maybe_rect, maybe_friends)
                break

        if eaten:
            del touching[maybe_rect]
            maybe_friends.append((x, y, d, t))
            touching[rect.Rect(*maybe_rect).union(r).to_tuple()] = maybe_friends
        else:
            touching[r.to_tuple()] = [(x, y, d, t)]

    # TODO: tiles might not be joined optimally. e.g. consider block growing left and block
    #  growing right - even though they're touching, they started out not touching, so they
    #  are separate in the list.

    # produce StaticObjects from groups of touching tiles
    static_objects = []
    for k, v in touching.iteritems():
        r = rect.Rect(*k)
        static_objects.append(static_object.StaticObject(r.x, r.y, r.width, r.height,
                                                         _render_static(r, v, tileset_seq, grid_width, grid_height)))

    return static_objects


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

    coll_grid = _produce_collision(_get_mid_grids(map_grid), width, height)

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
                    self.grid[layer_name][y].append(Tile(layer, self.coll_grid, self, (x, y)))

        self.objects = {}
        self.static_objects = _produce_statics_for_mid_grids(_get_mid_grids(tile_type_grid), self.tileset_seq,
                                                             self.grid_width, self.grid_height)

        self.cutscenes = {}
        self.active_cutscene = None

        self.triggers = {}

        self.fears_dict = {}

    def reset_fears_dict(self):
        from gslib import map_edit
        self.fears_dict = {'player': []} # dictionary to keep track of what objects have which .fears
        for f in map_edit.get_fears_from_file():
            self.fears_dict[f] = []
