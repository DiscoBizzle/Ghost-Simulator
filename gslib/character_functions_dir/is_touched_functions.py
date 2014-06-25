from __future__ import absolute_import, division, print_function
from AI_functions import BaseFunction

__author__ = 'Martin'


class IsTouchedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(IsTouchedFunction, self).__init__(name, obj, 'is_touched_function', 'is_touched_functions')



class ActivateOnFire(IsTouchedFunction):
    def __init__(self, obj):
        super(ActivateOnFire, self).__init__("Activate On Fire", obj)

    def function(self, toucher):
        obj = self.object
        for p in toucher.held_objects:
            if 'fire' in p.properties:
                obj.activate()
                return


class BePickedUp(IsTouchedFunction):
    def __init__(self, obj):
        super(BePickedUp, self).__init__("Be Picked Up", obj)

    def function(self, toucher):
        obj = self.object
        if not obj.can_be_picked_up:
            return
        if hasattr(toucher, 'held_objects'):
            obj.held_by = toucher

# def activate_on_fire(obj):
#     def func(toucher):  # need to accept toucher, even if this function don't need it!
#         for p in toucher.held_objects:
#             if 'fire' in p.properties:
#                 obj.activate()
#                 return
#     func.__name__ = 'activate_on_fire'
#     return func
#
# def be_picked_up(obj):
#     def func(toucher):  # need to accept toucher, even if this function don't need it!
#         if not obj.can_be_picked_up:
#             return
#         if hasattr(toucher, 'held_objects'):
#             obj.held_by = toucher
#     func.__name__ = 'be_picked_up'
#     return func