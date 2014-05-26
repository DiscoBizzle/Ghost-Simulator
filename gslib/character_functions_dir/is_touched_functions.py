from __future__ import absolute_import, division, print_function

__author__ = 'Martin'


def activate_on_fire(obj):
    def func(toucher):  # need to accept toucher, even if this function don't need it!
        for p in toucher.held_props:
            if 'fire' in p.properties:
                obj.activate()
                return
    func.__name__ = 'activate_on_fire'
    return func

def be_picked_up(obj):
    def func(toucher):  # need to accept toucher, even if this function don't need it!
        if not obj.can_be_picked_up:
            return
        if hasattr(toucher, 'held_props'):
            obj.held_by = toucher
    func.__name__ = 'be_picked_up'
    return func