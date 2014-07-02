from __future__ import absolute_import, division, print_function

__author__ = 'Martin'

import random
import math
from gslib.character_functions.base_function import BaseFunction

################################################################################
### scared functions
################################################################################

class ScaredFunction(BaseFunction):
    def __init__(self, name, obj):
        super(ScaredFunction, self).__init__(name, obj, 'feared_function', 'when_scared_functions')


class Panic(ScaredFunction):
    def __init__(self, obj):
        super(Panic, self).__init__("Panic", obj)

    def function(self, _):
        obj = self.object
        obj.current_speed = obj.feared_speed

        obj.move_down = False
        obj.move_up = False
        obj.move_left = False
        obj.move_right = False
        if random.randint(0, 1):
            obj.move_down = True
        else:
            obj.move_up = True

        if random.randint(0, 1):
            obj.move_right = True
        else:
            obj.move_left = True



class Freeze(ScaredFunction):
    def __init__(self, obj):
        super(Freeze, self).__init__("Freeze", obj)

    def function(self, _):
        obj = self.object
        obj.current_speed = 0



class RunAwayStraight(ScaredFunction):
    def __init__(self, obj):
        super(RunAwayStraight, self).__init__("Run Away Straight", obj)

    def function(self, _):
        obj = self.object
        obj.current_speed = obj.feared_speed
        vec = (obj.coord[0] - obj.feared_from_pos[0], obj.coord[1] - obj.feared_from_pos[1])
        if vec[0] == 0:
            if vec[1] >= 0:
                ang = 90.0
            else:
                ang = -90.0
        else:
            ang = math.atan(vec[1] / vec[0]) * 180 / math.pi

        if vec[0] < 0:
            ang += 180.0

        obj.move_down = False
        obj.move_up = False
        obj.move_left = False
        obj.move_right = False

        if -22.5 <= ang <= 22.5:
            obj.move_right = True
            return
        if 22.5 <= ang <= 67.5:
            obj.move_right = True
            obj.move_up = True
            return
        if 67.5 <= ang <= 112.5:
            obj.move_up = True
            return
        if 112.5 <= ang <= 157.5:
            obj.move_up = True
            obj.move_left = True
            return
        if 157.5 <= ang <= 202.5:
            obj.move_left = True
            return
        if 202.5 <= ang <= 247.5:
            obj.move_left = True
            obj.move_down = True
            return
        if ang >= 247.5 or ang <= -67.5:
            obj.move_down = True
            return
        if -67.5 <= ang <= -22.5:
            obj.move_right = True
            obj.move_down = True
            return
