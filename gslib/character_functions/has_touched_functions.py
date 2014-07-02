from __future__ import absolute_import, division, print_function
from gslib.character_functions.base_function import BaseFunction

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
