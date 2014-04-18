from gslib import character_functions



################################################################################
### triggers - links character objects
### E.g. Do thing to B when A does x.
### REQUIRED:
### - legend with correct number of entries
### - default objects values is None
################################################################################
class Trigger(object):
    def __init__(self, m, trigger_func, objects):
        self.func = trigger_func
        self.object_references = objects
        self.legend = (u'Object 1', u'Object 2')

        if not objects[0] is None:  # make the trigger if objects were passed in
            self.objects = [m.objects[o] for o in objects]
            self.func(*self.objects)
        else:  # set objects to list for reasons of editor making new trigger at runtime
            self.objects = []


class FlipStateOnHarvest(Trigger):
    def __init__(self, m, harvestee=None, target=None):
        """
        target flips character state when harvestee has fear harvested
        """
        Trigger.__init__(self, m, trigger_flip_state_on_harvest, (harvestee, target))

        self.legend = (u'Harvestee', u'Target')


class FlipStateWhenTouchedConditional(Trigger):
    """
    target flips character state when toucher comes into contact with touched
    """
    def __init__(self, m, toucher=None, touched=None, target=None):
        Trigger.__init__(self, m, trigger_flip_state_is_touched_by, (toucher, touched, target))

        self.legend = (u'Toucher', u'Touched', u'Target')


class FlipStateWhenUnTouchedConditional(Trigger):
    """
    target flips character state when toucher loses contact with touched
    """
    def __init__(self, m, untoucher=None, untouched=None, target=None):
        Trigger.__init__(self, m, trigger_flip_state_is_untouched_by, (untoucher, untouched, target))

        self.legend = (u'Untoucher', u'Untouched', u'Target')


possible_triggers = {'Flip State On Harvest': FlipStateOnHarvest,
                     'Flip State When Touched (Conditional)': FlipStateWhenTouchedConditional,
                     'Flip State When UnTouched (Conditional)': FlipStateWhenUnTouchedConditional}

# Game events that can call functions:
# - feared_function - executed every tick when the character is scared
# - possessed_function - occurs when the character becomes possessed
# - unpossessed_function - occurs when the character becomes unpossessed
# - harvested_function - when the character has had its fear harvested (ooga booga'd)
# - is_touched_function - when the charcter is touched; accepts input of object that touched it
# - is_untouched_function - when the charcter is untouched; accepts input of object that untouched it
# - has_touched_function - when the character touches an object; accepts input of of object that it touches
# - has_untouched_function - when the character untouches an object; accepts input of of object that it untouches

# Make sure 'trigger' occurs in the func.__name__ (and doesn't occur in the other function types)
def trigger_flip_state_on_harvest(obj, target):
    def func(harvester):
        character_functions.flip_state(target)(harvester)
    func.__name__ = 'trigger_flip_state_on_harvest'
    obj.harvested_function.append(func)


def trigger_flip_state_is_touched_by(toucher, touched, target):
    def func(o):
        if o == toucher:
            character_functions.flip_state(target)(o)
    func.__name__ = 'trigger_flip_state_is_touched_by'
    touched.is_touched_function.append(func)


def trigger_flip_state_is_untouched_by(untoucher, untouched, target):
    def func(o):
        if o == untoucher:
            character_functions.flip_state(target)(o)
    func.__name__ = 'trigger_flip_state_is_untouched_by'
    untouched.is_untouched_function.append(func)