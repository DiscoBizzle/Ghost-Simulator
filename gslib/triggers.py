from __future__ import absolute_import, division, print_function

# from gslib import character_functions
from gslib import trigger_functions
from gslib import rect
import json


# get all functions from trigger_functions module
trigger_functions_dict = {}
for i, s in enumerate(dir(trigger_functions)):
    f = getattr(trigger_functions, s)
    if hasattr(f, '__call__'): # check if it is a function
        trigger_functions_dict[unicode(s)] = f  # fill temp dict with 'function_name': function

# decorator to make a called function conditional
def conditional(desired_interacter):
    def check_interacter(func):
        def new_func(interactee, interacter):
            if interacter == desired_interacter:
                func(interactee, interacter)
        new_func.func_name = func.func_name
        return new_func
    return check_interacter


class Trigger(object):
    def __init__(self, game, object_refs, actions=None):
        if not hasattr(self, 'func_type'):
            self.func_type = None

        if not hasattr(self, 'conditional'):
            self.conditional = False

        if object_refs[0] is None:  # set objects to list for reasons of editor making new trigger at runtime
            self.object_references = []
            self.objects = []
        else:   # make the trigger if objects were passed in
            self.object_references = object_refs
            self.objects = [game.objects[o] for o in object_refs]
            getattr(self.objects[-2], self.func_type).append(self.perf_actions)

        if actions is None: # the list of functions to do to target when triggered
            self.actions = []
        else:
            self.actions = []
            for a in actions:
                self.add_action(a)

        self.legend = (u'Object 1', u'Object 2')

    def add_action(self, action):
        if action is None:
            return
        if self.conditional:
            act = action(self.objects[-1])
            cond_act = conditional(self.objects[0])(act)
            self.actions.append(cond_act)
        else:
            self.actions.append(action(self.objects[-1])) # last object is Target

    def perf_actions(self, interacter):
        for a in self.actions:
            a(self.objects[-2], interacter)

    def create_save_dict(self):
        save_dict = {}
        save_dict[u'object_references'] = self.object_references

        act_list = [f.__name__ for f in self.actions]

        save_dict[u'actions'] = json.dumps(act_list)

        save_dict[u'trigger_type'] = self.__class__.__name__

        return save_dict

    def __del__(self):
        if len(self.objects) >= 2:
            o_funcs = getattr(self.objects[-2], self.func_type)
            o_funcs.remove(self.perf_actions)


class TriggerZone(Trigger):
    def __init__(self, game, object_refs, actions=None):
        Trigger.__init__(self, game, object_refs, actions)

        self._pos = (0, 0)
        self._size = (1, 1)
        self.zone = rect.Rect(self._pos, self._size)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        self._pos = p
        self.zone = rect.Rect(self._pos, self._size)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, s):
        self._size = s
        self.zone = rect.Rect(self._pos, self._size)

    def check_entry(self, prev_pos, obj):
        if self.conditional:
            if not obj == self.objects[0]:
                return False
        p = obj.coord
        if self.zone.collidepoint(p): # if is now in zone
            if not self.zone.collidepoint(prev_pos): # if wasnt in zone previously
                self.perf_actions(obj)


class TriggerZoneConditional(TriggerZone):
    def __init__(self, game, object_refs, actions=None):
        self.conditional = True
        super(TriggerZoneConditional, self).__init__(game, object_refs, actions)

################################################################################
### triggers - links character objects
### E.g. Do thing to B when A does x.
### REQUIRED:
### - legend with correct number of entries
### - default objects values is None
################################################################################

class OnHarvest(Trigger):
    def __init__(self, game, harvestee=None, target=None, actions=None):
        """
        when harvestee has fear harvested, do actions to target
        """
        self.func_type = 'harvested_function'
        Trigger.__init__(self, game, (harvestee, target), actions=actions)

        self.legend = (u'Harvestee', u'Target')

class OnHarvestConditional(Trigger):
    def __init__(self, game, harvester=None, harvestee=None, target=None, actions=None):
        """
        when harvestee has fear harvested, do actions to target, IFF interacter is correct
        """
        self.func_type = 'harvested_function'
        self.conditional = True
        Trigger.__init__(self, game, (harvester, harvestee, target), actions=actions)

        self.legend = (u'Harvester', u'Harvestee', u'Target')


class IsTouched(Trigger):
    def __init__(self, game, touched=None, target=None, actions=None):
        """
        when Touched is touched, do actions to Target
        """
        self.func_type = 'is_touched_function'
        Trigger.__init__(self, game, (touched, target), actions=actions)

        self.legend = (u'Touched', u'Target')

class IsTouchedConditional(Trigger):
    def __init__(self, game, toucher=None, touched=None, target=None, actions=None):
        """
        when Touched is touched by Toucher (only), do actions to Target
        """
        self.func_type = 'is_touched_function'
        self.conditional = True
        Trigger.__init__(self, game, (toucher, touched, target), actions=actions)

        self.legend = (u'Toucher', u'Touched', u'Target')


# Game events that can call functions: TODO add the rest of these with both conditional and unconditional
# - feared_function - executed every tick when the character is scared
# - possessed_function - occurs when the character becomes possessed
# - unpossessed_function - occurs when the character becomes unpossessed
# - harvested_function - when the character has had its fear harvested (ooga booga'd)
# - is_touched_function - when the charcter is touched; accepts input of object that touched it
# - is_untouched_function - when the charcter is untouched; accepts input of object that untouched it
# - has_touched_function - when the character touches an object; accepts input of of object that it touches
# - has_untouched_function - when the character untouches an object; accepts input of of object that it untouches


# TODO also add any new ones to save_load.trigger_type_map with *exact* class names
possible_triggers = {'On Harvest': OnHarvest,
                     'On Harvest (Conditional)': OnHarvestConditional,
                     'Is Touched': IsTouched,
                     'Is Touched (Conditional)': IsTouchedConditional}
