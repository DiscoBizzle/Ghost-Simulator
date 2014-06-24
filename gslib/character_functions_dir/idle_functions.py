__author__ = 'Martin'
import random
from AI_functions import BaseFunction


class StandStill(BaseFunction):
    def __init__(self, obj):
        super(StandStill, self).__init__("Stand Still", obj)

    def function(self):
        self.object.current_speed = 0

class MoveToPoint(BaseFunction):
    def __init__(self, obj):
        super(MoveToPoint, self).__init__("Move To Point", obj)

    def function(self): # move to first point in patrol path
        obj = self.object
        obj.current_speed = obj.normal_speed

        tpos = obj.patrol_path[0]
        cpos = obj.coord

        if tpos[0] > cpos[0]:
            obj.move_right = True
        else:
            obj.move_left = True

        if tpos[1] > cpos[1]:
            obj.move_up = True
        else:
            obj.move_down = True

# def stand_still(self, obj):
#     def func():
#         obj.current_speed = 0
#     func.__name__ = 'stand_still'
#     return func


# def move_to_point(obj): # move to first point in patrol path
#     def func():
#         obj.current_speed = obj.normal_speed
#
#         tpos = obj.patrol_path[0]
#         cpos = obj.coord
#
#         if tpos[0] > cpos[0]:
#             obj.move_right = True
#         else:
#             obj.move_left = True
#
#         if tpos[1] > cpos[1]:
#             obj.move_up = True
#         else:
#             obj.move_down = True
#     func.__name__ = 'move_to_point'
#     return func


def wander(obj):
    def func():
        obj.current_speed = random.randint(obj.min_speed, obj.normal_speed)

        if random.randint(0, 1):
            obj.move_down = True
        else:
            obj.move_up = True

        if random.randint(0, 1):
            obj.move_right = True
        else:
            obj.move_left = True
    func.__name__ = 'wander'
    return func


def patrol(obj):
    def func():
        obj.current_speed = obj.normal_speed

        tpos = obj.patrol_path[obj.patrol_index]
        cpos = obj.coord

        if tpos == cpos: # advance to next point in patrol
            obj.patrol_index += 1
            obj.patrol_index % len(obj.patrol_path)
            tpos = obj.patrol_path[obj.patrol_index]

        if tpos[0] > cpos[0]:
            obj.move_right = True
        else:
            obj.move_left = True

        if tpos[1] > cpos[1]:
            obj.move_up = True
        else:
            obj.move_down = True
    func.__name__ = 'patrol'
    return func