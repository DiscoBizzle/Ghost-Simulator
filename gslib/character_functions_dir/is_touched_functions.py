from __future__ import absolute_import, division, print_function

__author__ = 'Martin'


def activate_on_fire(obj):
    def func(toucher):  # need to accept toucher, even if this function don't need it!
        if 'torch' in toucher.flair.keys():
            obj.activate()
    func.__name__ = 'activate_on_fire'
    return func
