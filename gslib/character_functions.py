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


from when_harvested_functions import *
from when_scared_functions import *
from become_possessed_functions import *
from become_unpossessed_functions import *
from on_touch_functions import *


