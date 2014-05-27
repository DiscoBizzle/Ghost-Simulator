from gslib import game
from gslib.constants import *

import math


# basics are from first half of http://aigamedev.com/open/tutorials/clearance-based-pathfinding/
# TODO: http://aigamedev.com/open/tutorial/symmetry-in-pathfinding/#3JumpPointSearch


class NodeAttributes(object):

    def __init__(self, parent, weight):
        self.parent = parent
        self.weight = weight


class Pathfinder(object):

    def __init__(self):
        self._grid, self._min_x, self._min_y, self._max_x, self._max_y = None, None, None, None, None

    def _update_map(self):
        # TODO: lots of shit
        # TODO: calculate actual clearance values, not just '1' for everything
        # TODO: only update if necessary/time has passed since last search!
        self._min_x = 0
        self._min_y = 0
        self._max_y = len(game.map.coll_grid) - 1
        self._max_x = len(game.map.coll_grid[self._max_y]) - 1
        #self._max_y, self._max_x = 5, 5

        print(self._min_x, self._min_y, self._max_x, self._max_y)
        self._grid = [[(0 if game.map.coll_grid[y][x][0] else 1)
                       for x in range(self._min_x, self._max_x + 1)]
                      for y in range(self._min_y, self._max_y + 1)]

    def _get_clearance(self, t, max_push):
        # returns 0 if blocked.
        #print('t', t[0], ' / ', t[1], 'clearance: ', self._grid[t[1]][t[0]])
        return self._grid[t[1]][t[0]]

    def get_path(self, start_t, goal_t, size, max_push):
        # TODO: clock
        # TODO: sort search list, so that we are doing A* and not in fact dijkstra
        # TODO: if we can move straight there, do so.
        # TODO: object awareness
        # TODO: optimization
        # TODO: objects that can't be considered square...?

        self._update_map()

        # Make sure neither the start nor goal are blocked.
        # TODO: if goal is blocked, get as near as possible? maybe that logic should happen outside pathfinder.
        if not (self._min_x <= start_t[0] <= self._max_x and self._min_y <= start_t[1] <= self._max_y):
            print('Pathfinder: start_t outside bounds.')
            return None
        if not (self._min_x <= goal_t[0] <= self._max_x and self._min_y <= goal_t[1] <= self._max_y):
            print('Pathfinder: goal_t outside bounds.')
            return None
        if self._get_clearance(start_t, max_push) < size or self._get_clearance(goal_t, max_push) < size:
            # TODO: ensure this doesn't fail just because the moving object is in the start tile!
            print('Pathfinder: start/goal blocked.')
            return None
        if size < 1:
            raise Exception('Pathfinder: size is ' + str(size) + ', expected at least 1.')

        open_t = {start_t: NodeAttributes(None, 0)}
        closed_t = {}

        dist_sq = lambda p: (abs(p[0] - start_t[0]) ** 2) + (abs(p[1] - start_t[1]) ** 2)
        cmp_k = lambda a, b: cmp(dist_sq(a), dist_sq(b))

        while len(open_t) > 0:
            # TODO: find & use an always sorted dict that sorts on insert
            s_k = sorted(open_t.keys(), cmp_k)[0]
            o_t, o_t_v = s_k, open_t.pop(s_k)
            print(len(open_t))

            if o_t == goal_t:
                # build & return path
                p = o_t_v.parent
                path = [o_t]
                while p is not None:
                    path.insert(0, p)
                    p = closed_t[p].parent
                return path
            else:
                o_t_x, o_t_y = o_t
                for o_t_neigh in [(x, y) for x in range(o_t_x - 1, o_t_x + 2) for y in range(o_t_y - 1, o_t_y + 2)]:
                    # out of bounds?
                    if not (self._min_x <= o_t_neigh[0] <= self._max_x and self._min_y <= o_t_neigh[1] <= self._max_y):
                        continue
                    # self?
                    if o_t_neigh == o_t:
                        continue

                    add_cost = 1

                    if o_t_neigh in closed_t:
                        # already searched; skip
                        continue
                    elif o_t_neigh in open_t:
                        # "if neighbour is already on the open list, update weights"
                        if open_t[o_t_neigh].weight > o_t_v.weight + add_cost:
                            open_t[o_t_neigh] = NodeAttributes(o_t, o_t_v.weight + add_cost)
                    elif self._get_clearance(o_t_neigh, max_push - 0) >= size:
                        # TODO: sorted insert!! (a* not dijkstra)
                        open_t[o_t_neigh] = NodeAttributes(o_t, o_t_v.weight + add_cost)
                    else:
                        continue

            closed_t[o_t] = o_t_v

        return None
