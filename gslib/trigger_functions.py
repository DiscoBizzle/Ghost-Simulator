__author__ = 'Martin'
from gslib import graphics


# IMPORTANT: Name these functions with 'trigger' in the name, for reasons of saving.

def flip_state_trigger(targets):
    def func(interactee, interacter):
        for target in targets:
            target.state_index = str((int(target.state_index) + 1) % len(target.states))
    func.__name__ = 'flip_state_trigger'
    return func

def red_square_trigger(targets):
    def func(interactee, interacter):
        for target in targets:
            target.fear = 0
            target.fainted = True

            sprite = graphics.new_rect_sprite()
            sprite.scale_x = 10
            sprite.scale_y = 10
            sprite.color_rgb = (120, 0, 0)
            target.flair['fear_harvested'] = (sprite, (-5, target.dimensions[1] + 5))
    func.__name__ = 'red_square_trigger'
    return func

def activate_trigger(targets):
    def func(interactee, interacter):
        for target in targets:
            target.activate()
    func.__name__ = 'activate_trigger'
    return func