__author__ = 'Martin'

from gslib.game_objects.prop import Prop

class Torch(Prop):
    def __init__(self, game, x=0, y=0):
        super(Torch, self).__init__(game, x, y, 32, 16, sprite_height=32, sprite_width=16, sprite_sheet="props/torch.png")

        self.properties = ['fire']

        self.centre_offset = (8, 0)

    def _update_animation(self):
        pass



possible_props = {'Torch': Torch}