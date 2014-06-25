from __future__ import absolute_import, division, print_function
from gslib.character_functions_dir.base_function import BaseFunction

__author__ = 'Martin'


class IsUntouchedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(IsUntouchedFunction, self).__init__(name, obj, 'is_untouched_function', 'is_untouched_functions')
