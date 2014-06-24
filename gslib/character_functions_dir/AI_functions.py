__author__ = 'Martin'

class BaseFunction(object):
    def __init__(self, name, obj):
        self.name = name
        self.object = obj

        self.number_coordinates = 0 # Number of expected coordinates, set to -1 for infinite

        self.options = {'text': [], 'coordinates': []}

    def function(self):
        pass