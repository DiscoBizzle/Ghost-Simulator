from __future__ import absolute_import, division, print_function

from gslib.constants import *


class ObjectCollisionLookup(object):

    def __init__(self, game):
        self.grid = None
        self.game = game

    def candidates_for(self, search_rect):
        ni = search_rect.left // TILE_SIZE
        nj = search_rect.bottom // TILE_SIZE

        if 0 <= ni < LEVEL_WIDTH // TILE_SIZE and 0 <= nj < LEVEL_HEIGHT // TILE_SIZE:
            if len(self.grid[nj][ni]) > 0:
                return set(self.grid[nj][ni])

        return set()

    def update_all(self):
        #if not self.lazy_grid:
        # reset lazy object collision grid
        self.grid = [[[] for x in range(0, self.game.map.grid_width)] for y in range(0, self.game.map.grid_height)]

        # update lazy object collision grid
        for obj in self.game.objects.itervalues():
            self._update_for(obj)

    def _update_for(self, obj):
        if self.grid and obj.collision_weight != 0:
            b_x = obj.coord[0] // TILE_SIZE
            b_y = obj.coord[1] // TILE_SIZE
            for ny in range(b_y - 1, b_y + 2):
                for nx in range(b_x - 1, b_x + 2):
                    if 0 <= nx < LEVEL_WIDTH // TILE_SIZE and 0 <= ny < LEVEL_HEIGHT // TILE_SIZE:
                        self.grid[ny][nx].append(obj)
                        #obj.in_grid = True

    def update_for(self, obj):
        # Unfortunately this is relatively slow.
        # Right now we instead try to put objects in the grid over-eagerly, and never update mid-frame.
        # This should work while our assumption that objects are max 2x2 tiles and have slow move speeds is true.
        #self._update_for(obj)
        return
