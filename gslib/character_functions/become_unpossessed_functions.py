from __future__ import absolute_import, division, print_function
from gslib.character_functions.base_function import BaseFunction

__author__ = 'Martin'

################################################################################
### unpossession functions
### These happen when a character is unpossessed
################################################################################

class BecomeUnpossessedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(BecomeUnpossessedFunction, self).__init__(name, obj, 'unpossessed_functions', 'become_unpossessed_functions')


class AdvanceState(BecomeUnpossessedFunction): # advances through states that are purely numerical, starting from 0 (need to be strings)
    def __init__(self, obj):
        super(AdvanceState, self).__init__('Advance State', obj)

    def function(self, unpossessor):
        obj = self.object
        obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))
