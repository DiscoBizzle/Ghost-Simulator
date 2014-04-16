__author__ = 'Martin'

import random
import math

################################################################################
### scared functions
################################################################################
def panic(obj):
    def func():
        obj.current_speed = 10

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

    func.__name__ = 'panic'
    return func


def freeze(obj):
    def func():
        obj.current_speed = 0
    func.__name__ = 'freeze'
    return func


def run_away_straight(obj):
    def func():
        obj.current_speed = 10
        vec = (obj.coord[0] - obj.feared_from_pos[0], obj.coord[1] - obj.feared_from_pos[1])
        if vec[0] == 0:
            if vec[1] >= 0:
                ang = 90.0
            else:
                ang = -90.0
        else:
            ang = math.atan(vec[1]/float(vec[0])) * 180 / math.pi

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
            obj.move_down = True
            return
        if 67.5 <= ang <= 112.5:
            obj.move_down = True
            return
        if 112.5 <= ang <= 157.5:
            obj.move_down = True
            obj.move_left = True
            return
        if 157.5 <= ang <= 202.5:
            obj.move_left = True
            return
        if 202.5 <= ang <= 247.5:
            obj.move_left = True
            obj.move_up = True
            return
        if ang >= 247.5 or ang <= -67.5:
            obj.move_up = True
            return
        if -67.5 <= ang <= -22.5:
            obj.move_right = True
            obj.move_up = True
            return
    func.__name__ = 'run_away_straight'
    return func

