from gslib import fear_functions


class Trigger(object):
    def __init__(self, trigger_func, objects=None):
        self.func = trigger_func
        self.objects = objects
        self.legend = (u'Object 1', u'Object 2')


class FlipStateOnHarvest(Trigger):
    def __init__(self, (harvestee, target)):
        """
        target flips character state when harvestee has fear harvested
        """
        Trigger.__init__(self, trigger_flip_state_on_harvest, (harvestee, target))

        self.legend = (u'Harvestee', u'Target')
        self.func(self.objects[0], self.objects[1])


class FlipStateWhenTouchedConditional(Trigger):
    """
    target flips character state when toucher comes into contact with touched
    """
    def __init__(self, (toucher, touched, target)):
        Trigger.__init__(self, trigger_flip_state_is_touched_by, (toucher, touched, target))

        self.legend = (u'Toucher', u'Touched', u'Target')
        self.func(self.objects[0], self.objects[1], self.objects[2])


class FlipStateWhenUnTouchedConditional(Trigger):
    """
    target flips character state when toucher loses contact with touched
    """
    def __init__(self, (untoucher, untouched, target)):
        Trigger.__init__(self, trigger_flip_state_is_untouched_by, (untoucher, untouched, target))

        self.legend = (u'Untoucher', u'Untouched', u'Target')
        self.func(self.objects[0], self.objects[1], self.objects[2])






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