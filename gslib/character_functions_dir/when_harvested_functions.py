from __future__ import absolute_import, division, print_function
from gslib.engine import primitives
from gslib.character_functions_dir.base_function import BaseFunction

__author__ = 'Martin'


################################################################################
### fear harvested functions
################################################################################


class HarvestedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(HarvestedFunction, self).__init__(name, obj, 'harvested_function', 'when_harvested_functions')


class RedSquare(HarvestedFunction):
    def __init__(self, obj):
        super(RedSquare, self).__init__("Red Square", obj)

    def function(self, harvester):
        obj = self.object
        obj.fear = 0
        obj.fainted = True

        sprite = primitives.RectPrimitive(width=10, height=10, color=(120, 0, 0, 255))
        obj.flair['fear_harvested'] = (sprite, (-5, obj.dimensions[1] + 5))


# def red_square(obj):  # get ooga booga'd
#     def func(harvester):
#         obj.fear = 0
#         obj.fainted = True
#
#         sprite = primitives.RectPrimitive(width=10, height=10, color=(120, 0, 0, 255))
#         obj.flair['fear_harvested'] = (sprite, (-5, obj.dimensions[1] + 5))
#     func.__name__ = 'red_square'
#     return func
