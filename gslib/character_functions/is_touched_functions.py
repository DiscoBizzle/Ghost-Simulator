from __future__ import absolute_import, division, print_function
from gslib.character_functions.base_function import BaseFunction

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
