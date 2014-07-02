from __future__ import absolute_import, division, print_function
__author__ = 'Martin'


class BaseFunction(object):
    def __init__(self, name, obj, typ, module_name):
        self.name = name
        self.object = obj
        self.function_type = typ # typ is the exact name of the attribute used in the character version of this function type
        self.module_name = module_name # module name is the name of the module for that attribute's functions (for save/load purposes)

        self.number_coordinates = 0 # Number of expected coordinates, set to -1 for infinite

        self.text_options = []
        self.active_text_options = {} # set of options

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

        return self.module_name, self.__class__.__name__, d

    def load_from_dict(self, d):
        self.coordinates = d['coordinates']
        self.active_text_options = d['active_text_options']
        self.current_coordinate_index = d['current_coordinate_index']
        self.module_name = d['module_name']
