from __future__ import absolute_import, division, print_function
import random
from gslib.character_functions.base_function import BaseFunction

__author__ = 'Martin'

class IdleFunction(BaseFunction):
    def __init__(self, name, obj):
        super(IdleFunction, self).__init__(name, obj, 'idle_functions', 'idle_functions')



class StandStill(IdleFunction):
    def __init__(self, obj):
        super(StandStill, self).__init__("Stand Still", obj)

    def function(self, other):
        self.object.current_speed = 0


class MoveToPoint(IdleFunction):
    def __init__(self, obj):
        super(MoveToPoint, self).__init__("Move To Point", obj)
        self.number_coordinates = 1

    def function(self, other):
        if len(self.coordinates) == 0: # no target point selected
            return

        obj = self.object
        obj.current_speed = obj.normal_speed

        tpos = self.coordinates[0]
        cpos = obj.coord

        if tpos[0] > cpos[0]:
            obj.move_right = True
        else:
            obj.move_left = True

        if tpos[1] > cpos[1]:
            obj.move_up = True
        else:
            obj.move_down = True


class Wander(IdleFunction):
    def __init__(self, obj):
        super(Wander, self).__init__("Wander", obj)

    def function(self, other):
        obj = self.object
        obj.current_speed = random.randint(obj.min_speed, obj.normal_speed)

        if random.randint(0, 1):
            obj.move_down = True
        else:
            obj.move_up = True

        if random.randint(0, 1):
            obj.move_right = True
        else:
            obj.move_left = True


class Patrol(IdleFunction):
    def __init__(self, obj):
        super(Patrol, self).__init__("Patrol", obj)
        self.number_coordinates = -1

    def function(self, other):
        if len(self.coordinates) == 0: # no target coordinates
            return

        obj = self.object
        obj.current_speed = obj.normal_speed

        tpos = self.coordinates[self.current_coordinate_index]
        cpos = obj.coord

        if (tpos[0] - cpos[0])**2 + (tpos[1] - cpos[1])**2 < 2500: # advance to next point in patrol
            self.current_coordinate_index += 1
            self.current_coordinate_index %= len(self.coordinates)
            self.function(other) # advance to coordinate just changed to

        if tpos[0] > cpos[0]: # TODO make this follow pathfinding
            obj.move_right = True
        else:
            obj.move_left = True

        if tpos[1] > cpos[1]:
            obj.move_up = True
        else:
            obj.move_down = True

