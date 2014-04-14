from gslib import fear_functions


################################################################################
### triggers - links character objects
### E.g. Do thing to B when A does x.
### REQUIRED:
### - legend with correct number of entries
### - default objects values is None
################################################################################
class Trigger(object):
    def __init__(self, trigger_func, objects):
        self.func = trigger_func
        self.objects = objects
        self.legend = (u'Object 1', u'Object 2')

        if self.objects[0]:  # make the trigger if objects were passed in
            self.func(*self.objects)
        else:  # set objects to list for reasons of editor making new trigger at runtime
            self.objects = []


class FlipStateOnHarvest(Trigger):
    def __init__(self, harvestee=None, target=None):
        """
        target flips character state when harvestee has fear harvested
        """
        Trigger.__init__(self, trigger_flip_state_on_harvest, (harvestee, target))

        self.legend = (u'Harvestee', u'Target')


class FlipStateWhenTouchedConditional(Trigger):
    """
    target flips character state when toucher comes into contact with touched
    """
    def __init__(self, toucher=None, touched=None, target=None):
        Trigger.__init__(self, trigger_flip_state_is_touched_by, (toucher, touched, target))

        self.legend = (u'Toucher', u'Touched', u'Target')


class FlipStateWhenUnTouchedConditional(Trigger):
    """
    target flips character state when toucher loses contact with touched
    """
    def __init__(self, untoucher=None, untouched=None, target=None):
        Trigger.__init__(self, trigger_flip_state_is_untouched_by, (untoucher, untouched, target))

        self.legend = (u'Untoucher', u'Untouched', u'Target')


# Game events that can call functions:
# - feared_function - executed every tick when the character is scared
# - possessed_function - occurs when the character becomes possessed
# - unpossessed_function - occurs when the character becomes unpossessed
# - harvested_function - when the character has had its fear harvested (ooga booga'd)
# - is_touched_function - when the charcter is touched; accepts input of object that touched it
# - is_untouched_function - when the charcter is untouched; accepts input of object that untouched it
# - has_touched_function - when the character touches an object; accepts input of of object that it touches
# - has_untouched_function - when the character untouches an object; accepts input of of object that it untouches


def trigger_flip_state_on_harvest(obj, target):
    def func():
        fear_functions.flip_state(target)()
    obj.harvested_function.append(func)


def trigger_flip_state_is_touched_by(toucher, touched, target):
    def func(o):
        if o == toucher:
            fear_functions.flip_state(target)()
    touched.is_touched_function.append(func)


def trigger_flip_state_is_untouched_by(untoucher, untouched, target):
    def func(o):
        if o == untoucher:
            fear_functions.flip_state(target)()
    untouched.is_untouched_function.append(func)