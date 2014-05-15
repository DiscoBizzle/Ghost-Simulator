# No bitchin' about returning functions, it makes triggers easier to think about/create.

# Game events that can call these functions:
# - feared_function - executed every tick when the character is scared
# - possessed_function - occurs when the character becomes possessed
# - unpossessed_function - occurs when the character becomes unpossessed
# - harvested_function - when the character has had its fear harvested (ooga booga'd)
# - is_touched_function - when the charcter is touched; accepts input of object that touched it
# - is_untouched_function - when the charcter is untouched; accepts input of object that untouched it
# - has_touched_function - when the character touches an object; accepts input of of object that it touches
# - has_untouched_function - when the character untouches an object; accepts input of of object that it untouches

from __future__ import absolute_import, division, print_function

# these are needed so you can access the functions easily elsewhere
from gslib.character_functions_dir.become_unpossessed_functions import *
from gslib.character_functions_dir.has_touched_functions import *
from gslib.character_functions_dir.become_possessed_functions import *
from gslib.character_functions_dir.when_scared_functions import *
from gslib.character_functions_dir.when_harvested_functions import *

import pkgutil
import importlib
import os
import gslib.character_functions_dir

module_dict = {}
a =  os.path.dirname(gslib.character_functions_dir.__file__) + '/'
for _, m, _ in pkgutil.iter_modules([os.path.dirname(a)], prefix='gslib.character_functions_dir.'):
    mod = importlib.import_module(m)
    module_dict[mod] = dir(mod)


all_functions_dict = {}
temp_dict = {}
for k, v in module_dict.iteritems():
    temp_dict = {}
    for i, s in enumerate(v):
        f = getattr(k, s)
        if hasattr(f, '__call__'): # check if it is a function
            temp_dict[unicode(s)] = f  # fill temp dict with 'function_name': function
    all_functions_dict[unicode(str(k.__name__)[30:])] = temp_dict  # add 'module': {'function names': functions}, [30:] strips gslib.character_functions_dir

del temp_dict
del module_dict
