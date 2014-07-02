from __future__ import absolute_import, division, print_function

import io
import random
import os.path
import json

from gslib.engine import textures, text, sprite, primitives
from gslib.game_objects.game_object import GameObject
from gslib.constants import *


class Prop(GameObject):
    def __init__(self, game_class, x, y, w, h, **kwargs):
        """
        Props are much like characters, but cannot be made to walk when possessed.
        They are by default automatically picked up by characters on touch.
        They cannot pick things up.
        """
        super(Prop, self).__init__(game_class, x, y, w, h, **kwargs)
        self.possessed_function = []
        self.unpossessed_function = []
        self.idle_functions = [character_functions.stand_still(self)]

        self.properties = []

        self.centre_offset = (0, 0)

        self.patrol_path = []
        self.patrol_index = 0

        self.possessed_by = []

        self.can_be_picked_up = True
        self._held_by = None # name of object that holds this prop

        self._collision_weight = self.collision_weight

        self.is_touched_function.append(character_functions.be_picked_up(self))

        self._to_save = {'possessed_function', 'unpossessed_function', 'normal_speed',
                         'is_touched_function', 'is_untouched_function',
                         'states', 'coord', 'collision_weight', 'idle_functions', 'patrol_path', 'patrol_index',
                         'held_by', 'can_be_picked_up', 'centre_offset'}

    @property
    def collision_weight(self):
        if self._held_by is None:
            return self._collision_weight
        else:
            return 0

    @collision_weight.setter
    def collision_weight(self, val):
        self._collision_weight = val

    @property
    def held_by(self):
        return self._held_by

    @held_by.setter
    def held_by(self, obj):
        if obj is None:
            self._held_by = None
            return
        o_name = self.game_class.map.find_name_of_object(obj)
        self._held_by = o_name
        self.game_class.map.objects[o_name].held_objects.append(self)

    def update(self, dt):

        if not self.cutscene_controlling:
            self.update_timer += 1
            #pick random direction (currently only one of 8 directions, but at a random speed)

            if not self.held_by is None:
                held_o = self.game_class.objects[self.held_by]
                self.current_speed = 0
                self.coord = held_o.coord[0] + self.centre_offset[0], held_o.coord[1] + self.centre_offset[1]

            elif self.update_timer >= 50 and not self.fear_timer:
                self.update_timer = 0

                self.move_down = False
                self.move_up = False
                self.move_left = False
                self.move_right = False

                for i in self.idle_functions:
                    i()

            if self.possessed_by:
                for p in self.possessed_by:
                    p.coord = self.coord



        GameObject.update(self, dt)


    def create_save_dict(self):
        to_save = self._to_save

        save_dict = {}
        for s in to_save:
            o = getattr(self, s)
            if isinstance(o, list):
                if o:
                    if hasattr(o[0], '__call__'): # check if function
                        t_list = [f.__name__ for f in o]
                        save_dict[s] = json.dumps(t_list)
                        continue

            if s == u'fears':
                o = list(o)
            save_dict[s] = json.dumps(o)

        save_dict[u'object_type'] = self.__class__.__name__ + '_prop'
        return save_dict

    def load_from_dict(self, d):

        function_type_map = {'has_touched_function': u'has_touched_functions',
                     'feared_function': u'when_scared_functions',
                     'possessed_function': u'become_possessed_functions',
                     'unpossessed_function': u'become_unpossessed_functions',
                     'harvested_function': u'when_harvested_functions',
                     'is_touched_function': u'is_touched_functions',
                     'has_untouched_function': u'has_untouched_functions',
                     'is_untouched_function': u'is_untouched_functions',
                     'idle_functions': u'idle_functions'}

        for k, v in d.iteritems():
            if '_function' in k:
                func_list = json.loads(v)
                afd = character_functions.all_functions_dict
                attr = getattr(self, k)
                func_names = [a.__name__ for a in attr]
                for f in func_list:
                    if not 'trigger' in f and not 'perf_actions' in f:
                        if not f in func_names:
                            function_type = afd[function_type_map[k]]
                            attr.append(function_type[f](self))
            elif k != u'object_type':
                if k == u'fears':
                    fears = json.loads(v)
                    self.fears.extend(fears)
                setattr(self, k, json.loads(v))

    def activate(self):
        pass