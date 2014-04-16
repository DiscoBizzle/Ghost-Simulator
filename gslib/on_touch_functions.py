__author__ = 'Martin'

################################################################################
### touch functions
### These happen when a character is touched or untouched
################################################################################
def touched_flip_state(obj):
    def func(toucher):  # need to accept toucher, even if this function don't need it!
        obj.state_index = not obj.state_index
        # print obj.state_index
    return func