import pygame
import random
import math

from gslib import text_functions


################################################################################
### trigger functions
################################################################################
def trigger_flip_state_on_collection(obj, target):
    def func():
        red_square(obj)()
        flip_state(target)()
    obj.collected_function = func


def trigger_flip_state_is_touched_by(toucher, touched, target):
    def func(o):
        if o == toucher:
            flip_state(target)()
    touched.is_touched_function = func


def trigger_flip_state_is_untouched_by(untoucher, untouched, target):
    def func(o):
        if o == untoucher:
            flip_state(target)()
    untouched.is_untouched_function = func


################################################################################
### touch functions
### These happen when a character is touched (or untouched, to be added later)
################################################################################
def touched_flip_state(obj):
    def func(toucher):  # need to accept toucher, even if this function don't need it!
        obj.state_index = not obj.state_index
        # print obj.state_index
    return func


################################################################################
### possession functions
### These happen when a character is possessed or unpossessed
################################################################################
def im_possessed(obj):
    def func():
        surf = text_functions.speech_bubble("I'm possessed!", 150)
        pos = (obj.dimensions[0]/2,  - surf.get_height())
        obj.flair['possessed'] = (surf, pos)
    return func


def undo_im_possessed(obj):
    def func():
        del obj.flair['possessed']
    return func


def flip_state(obj):
    def func():
        obj.state_index = not obj.state_index
    return func


################################################################################
### fear collected functions
################################################################################
def red_square(obj):  # get ooga booga'd
    def func():
        obj.fear = 0
        obj.fainted = True
        surf = pygame.Surface((10, 10))
        surf.fill((120, 0, 0))
        obj.flair['fear_collected'] = (surf, (-5, -obj.dimensions[1] - 5))
    return func


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
    return func


def freeze(obj):
    def func():
        obj.current_speed = 0
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
    return func