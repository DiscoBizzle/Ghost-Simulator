from __future__ import absolute_import, division, print_function
from AI_functions import BaseFunction

__author__ = 'Martin'

################################################################################
### touch functions
### These happen when a character has touched or untouched
################################################################################

class HasTouchedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(HasTouchedFunction, self).__init__(name, obj, 'has_touched_function', 'has_touched_functions')


class FlipState(HasTouchedFunction):
    def __init__(self, obj):
        super(FlipState, self).__init__("Flip State", obj)

    def function(self, touched):
        obj = self.object
        obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))


class PickUp(HasTouchedFunction):
    def __init__(self, obj):
        super(PickUp, self).__init__("Pick Up", obj)

    def function(self, touched):
        obj = self.object
        if not touched.can_be_picked_up or not obj.can_pick_up:
            return

        touched.held_by = obj


# def touched_flip_state(obj):
#     def func(touched):  # need to accept toucher, even if this function don't need it!
#         obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))
#         # print obj.state_index
#     func.__name__ = 'touched_flip_state'
#     return func
#
# def try_pick_up(obj):
#     def func(touched):  # need to accept toucher, even if this function don't need it!
#         if not touched.can_be_picked_up or not obj.can_pick_up:
#             return
#
#         touched.held_by = obj
#     func.__name__ = 'be_picked_up'
#     return func