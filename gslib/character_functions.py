from gslib import graphics

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


import when_harvested_functions
import when_scared_functions
import become_possessed_functions
import become_unpossessed_functions
import has_touched_functions

from when_harvested_functions import *
from when_scared_functions import *
from become_possessed_functions import *
from become_unpossessed_functions import *
from has_touched_functions import *


module_dict = {when_harvested_functions: dir(when_harvested_functions),
                      when_scared_functions: dir(when_scared_functions),
                      become_possessed_functions: dir(become_possessed_functions),
                      become_unpossessed_functions: dir(become_unpossessed_functions),
                      has_touched_functions: dir(has_touched_functions)}

all_functions_dict = {}
temp_dict = {}
for k, v in module_dict.iteritems():
    v.remove('__author__')
    v.remove('__builtins__')
    v.remove('__doc__')
    v.remove('__file__')
    v.remove('__name__')
    v.remove('__package__')
    temp_dict = {}
    for i, s in enumerate(v):
        temp_dict[s] = getattr(k, s)  # fill temp dict with 'function_name': function
    all_functions_dict[str(k.__name__)[6:]] = temp_dict  # add 'module': {'function names': functions}, [6:] strips gslib.

del temp_dict
del module_dict
