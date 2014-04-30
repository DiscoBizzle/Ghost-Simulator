# from gslib import character_functions
from gslib import trigger_functions


# get all functions from trigger_functions module
trigger_functions_dict = {}
for i, s in enumerate(dir(trigger_functions)):
    f = getattr(trigger_functions, s)
    if hasattr(f, '__call__'): # check if it is a function
        trigger_functions_dict[unicode(s)] = f  # fill temp dict with 'function_name': function

# decorator to make a called function conditional
def conditional(desired_interacter):
    def check_interacter(func):
        def new_func(interacter):
            if interacter == desired_interacter:
                func(interacter)
        new_func.func_name = func.func_name
        return new_func
    return check_interacter


class Trigger(object):
    def __init__(self, game, object_refs):
        self.func_type = None
        self.actions = [] # the list of functions to do to target when triggered

        if object_refs[0] is None:  # set objects to list for reasons of editor making new trigger at runtime
            self.object_references = []
            self.objects = []
        else:   # make the trigger if objects were passed in
            self.object_references = object_refs
            self.objects = [game.objects[o] for o in object_refs]

        self.legend = (u'Object 1', u'Object 2')
        self.conditional = False

    def add_action(self, action):
        func = getattr(self.objects[-2], self.func_type) # second last object in list is Interactee
        if self.conditional:
            act = action(self.objects[-1])
            cond_act = conditional(self.objects[0])(act)
            func.append(cond_act)
        else:
            func.append(action(self.objects[-1])) # last object is Target


################################################################################
### triggers - links character objects
### E.g. Do thing to B when A does x.
### REQUIRED:
### - legend with correct number of entries
### - default objects values is None
################################################################################

class OnHarvest(Trigger):
    def __init__(self, game, harvestee=None, target=None):
        """
        when harvestee has fear harvested, do actions to target
        """
        Trigger.__init__(self, game, (harvestee, target))

        self.func_type = 'harvested_function'

        self.legend = (u'Harvestee', u'Target')

class OnHarvestConditional(Trigger):
    def __init__(self, game, harvester=None, harvestee=None, target=None):
        """
        when harvestee has fear harvested, do actions to target, IFF interacter is correct
        """
        Trigger.__init__(self, game, (harvester, harvestee, target))

        self.func_type = 'harvested_function'

        self.legend = (u'Harvester', u'Harvestee', u'Target')
        self.conditional = True


class IsTouched(Trigger):
    def __init__(self, game, touched=None, target=None):
        """
        when Touched is touched, do actions to Target
        """
        Trigger.__init__(self, game, (touched, target))

        self.func_type = 'is_touched_function'

        self.legend = (u'Touched', u'Target')

class IsTouchedConditional(Trigger):
    def __init__(self, game, toucher=None, touched=None, target=None):
        """
        when Touched is touched by Toucher (only), do actions to Target
        """
        Trigger.__init__(self, game, (toucher, touched, target))

        self.func_type = 'is_touched_function'

        self.legend = (u'Toucher', u'Touched', u'Target')
        self.conditional = True

# Game events that can call functions: TODO add the rest of these with both conditional and unconditional
# - feared_function - executed every tick when the character is scared
# - possessed_function - occurs when the character becomes possessed
# - unpossessed_function - occurs when the character becomes unpossessed
# - harvested_function - when the character has had its fear harvested (ooga booga'd)
# - is_touched_function - when the charcter is touched; accepts input of object that touched it
# - is_untouched_function - when the charcter is untouched; accepts input of object that untouched it
# - has_touched_function - when the character touches an object; accepts input of of object that it touches
# - has_untouched_function - when the character untouches an object; accepts input of of object that it untouches



possible_triggers = {'On Harvest': OnHarvest,
                     'On Harvest (Conditional)': OnHarvestConditional,
                     'Is Touched': IsTouched,
                     'Is Touched (Conditional)': IsTouchedConditional}
