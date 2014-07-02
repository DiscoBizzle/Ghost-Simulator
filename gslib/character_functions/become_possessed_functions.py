from __future__ import absolute_import, division, print_function
from gslib.character_functions.base_function import BaseFunction

__author__ = 'Martin'
################################################################################
### possession functions
### These happen when a character is possessed
################################################################################

class BecomePossessedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(BecomePossessedFunction, self).__init__(name, obj, 'possessed_functions', 'become_possessed_functions')


class AdvanceState(BecomePossessedFunction): # advances through states that are purely numerical, starting from 0 (need to be strings)
    def __init__(self, obj):
        super(AdvanceState, self).__init__('Advance State', obj)

    def function(self, possessor):
        obj = self.object
        obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))

