from __future__ import absolute_import, division, print_function

__author__ = 'Martin'

################################################################################
### unpossession functions
### These happen when a character is unpossessed
################################################################################

def undo_im_possessed(obj):
    def func(unpossessor):
        return
        if not obj.possessed_by:
            del obj.flair['possessed']
    func.__name__ = 'undo_im_possessed'
    return func


def flip_state(obj):
    def func(unpossessor):
        obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))
    func.__name__ = 'flip_state'
    return func
