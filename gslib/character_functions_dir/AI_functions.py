__author__ = 'Martin'

import inspect

import become_possessed_functions, become_unpossessed_functions, idle_functions, \
    has_touched_functions, has_untouched_functions, is_touched_functions, is_untouched_functions, \
    when_harvested_functions, when_scared_functions

class BaseFunction(object):
    def __init__(self, name, obj, typ, module_name):
        self.name = name
        self.object = obj
        self.function_type = typ # typ is the exact name of the attribute used in the character version of this function type
        self.module_name = module_name # module name is the name of the module for that attribute's functions (for save/load purposes)

        self.number_coordinates = 0 # Number of expected coordinates, set to -1 for infinite

        self.text_options = []
        self.active_text_options = []

        self.coordinates = []
        self.current_coordinate_index = 0

    def function(self, other_obj):
        pass

    def save_to_dict(self):
        d = {}
        d['active_text_options'] = self.active_text_options
        d['coordinates'] = self.coordinates
        d['current_coordinate_index'] = self.current_coordinate_index
        d['module_name'] = self.module_name

        return self.module_name, self.name, d

    def load_from_dict(self, d):
        self.coordinates = d['coordinates']
        self.active_text_options = d['active_text_options']
        self.current_coordinate_index = d['current_coordinate_index']
        self.module_name = d['module_name']


modules_list = [become_possessed_functions, become_unpossessed_functions, idle_functions,
                has_touched_functions, has_untouched_functions, is_touched_functions, is_untouched_functions,
                when_harvested_functions, when_scared_functions]

all_functions_dict = {}

for m in modules_list:
    funcs = {}
    for i, element in enumerate(dir(m)):
        f = getattr(m, element)
        if inspect.isclass(f):
            funcs[f.name] = f
    all_functions_dict[m.__name__] = funcs


def load_function(module_name, name, d):
    func = all_functions_dict[module_name][name].load_from_dict(d)
    return func