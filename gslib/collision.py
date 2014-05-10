from gslib.constants import *
from gslib import rect

class ObjectCollisionLookup(object):

    def __init__(self, game):
        self.grid = None
        self.game = game

    def candidates_for(self, search_rect):
        i = search_rect.left // TILE_SIZE
        j = search_rect.bottom // TILE_SIZE
        candidates = []

        for ni in range(i, i + 2):
            for nj in range(j, j + 2):
                if 0 <= ni < LEVEL_WIDTH // TILE_SIZE and 0 <= nj < LEVEL_HEIGHT // TILE_SIZE:
                    if len(self.grid[nj][ni]) > 0:
                        if rect.Rect((ni * TILE_SIZE, nj * TILE_SIZE), (TILE_SIZE, TILE_SIZE)).colliderect(search_rect):
                            candidates += self.grid[nj][ni]

        return set(candidates)

    def update_all(self):
        #if not self.lazy_grid:
        # reset lazy object collision grid
        self.grid = [[[] for x in range(0, self.game.map.grid_width)] for y in range(0, self.game.map.grid_height)]

        # update lazy object collision grid
        for obj in self.game.objects.itervalues():
            self.update_for(obj)

        """else:
            # update lazy object collision grid
            for obj in self.objects.itervalues():
                if obj.moved:
                    # remove from old squares
                    if obj.in_grid:
                        b_x = obj.last_coord[0] // TILE_SIZE
                        b_y = obj.last_coord[1] // TILE_SIZE
                        for ny in range(b_y - 1, b_y + 2):
                            for nx in range(b_x - 1, b_x + 2):
                                if 0 <= nx < LEVEL_WIDTH // TILE_SIZE and 0 <= ny < LEVEL_HEIGHT // TILE_SIZE:
                                    self.lazy_grid[ny][nx].remove(obj)
                    # add to new squares
                    b_x = obj.coord[0] // TILE_SIZE
                    b_y = obj.coord[1] // TILE_SIZE
                    for ny in range(b_y - 1, b_y + 2):
                        for nx in range(b_x - 1, b_x + 2):
                            if 0 <= nx < LEVEL_WIDTH // TILE_SIZE and 0 <= ny < LEVEL_HEIGHT // TILE_SIZE:
                                self.lazy_grid[ny][nx].append(obj)
                    obj.in_grid = True

        # move new to old
        for obj in self.objects.itervalues():
            obj.last_coord = obj.coord
            obj.moved = False"""

    def _update_for(self, obj):
        if self.grid:
            b_x = obj.coord[0] // TILE_SIZE
            b_y = obj.coord[1] // TILE_SIZE
            for ny in range(b_y - 2, b_y + 2):
                for nx in range(b_x - 2, b_x + 2):
                    if 0 <= nx < LEVEL_WIDTH // TILE_SIZE and 0 <= ny < LEVEL_HEIGHT // TILE_SIZE:
                        self.grid[ny][nx].append(obj)
                        #obj.in_grid = True

    def update_for(self, obj):
        # Unfortunately this is relatively slow.
        # Right now we instead try to put objects in the grid over-eagerly, and never update mid-frame.
        # This should work while our assumption that objects are max 2x2 tiles and have slow move speeds is true.
        #self._update_for(obj)
        return
