from __future__ import absolute_import, division, print_function
from gslib.character_functions.base_function import BaseFunction

__author__ = 'Martin'


class HasUntouchedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(HasUntouchedFunction, self).__init__(name, obj, 'has_untouched_function', 'has_untouched_functions')
