__author__ = 'Martin'

import graphics


################################################################################
### fear harvested functions
################################################################################
def red_square(obj):  # get ooga booga'd
    def func():
        obj.fear = 0
        obj.fainted = True

        sprite = graphics.new_rect_sprite()
        sprite.scale_x = 10
        sprite.scale_y = 10
        sprite.color_rgb = (120, 0, 0)
        obj.flair['fear_harvested'] = (sprite, (-5, obj.dimensions[1] + 5))
    return func