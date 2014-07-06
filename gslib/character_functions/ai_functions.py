from __future__ import absolute_import, division, print_function
__author__ = 'Martin'

import inspect

from gslib.character_functions import become_possessed_functions, become_unpossessed_functions, idle_functions, \
    has_touched_functions, has_untouched_functions, is_touched_functions, is_untouched_functions, \
    when_harvested_functions, when_scared_functions


modules_list = [become_possessed_functions, become_unpossessed_functions, idle_functions,
                has_touched_functions, has_untouched_functions, is_touched_functions, is_untouched_functions,
                when_harvested_functions, when_scared_functions]

all_functions_dict = {}

for m in modules_list:
    funcs = {}
    for i, element in enumerate(dir(m)):
        f = getattr(m, element)
        if inspect.isclass(f):
            if not "Function" in f.__name__:
                funcs[f.__name__] = f

    all_functions_dict[m.__name__[26:]] = funcs # cuts off "gslib.character_functions." from module name

    del funcs

def load_function(owner, module_name, name, d):
    func = all_functions_dict[module_name][name](owner)
    func.load_from_dict(d)
    return func


function_map = {'become_possessed_functions': 'possessed_function',
                     'become_unpossessed_functions': 'unpossessed_function',
                     'when_scared_functions': 'feared_function',
                     'has_touched_functions': 'has_touched_function',
                     'is_touched_functions': 'is_touched_function',
                     'has_untouched_functions': 'has_untouched_function',
                     'is_untouched_functions': 'is_untouched_function',
                     'when_harvested_functions': 'harvested_function',
                     'idle_functions': 'idle_functions'}
