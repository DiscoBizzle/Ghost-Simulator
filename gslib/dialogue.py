from gslib.constants import *
from gslib import graphics
from gslib import rect
from gslib import text


class SimpleDialogue(object):
    def __init__(self, game, message, on_complete_fun):
        self.game = game
        self.on_complete_fun = on_complete_fun
        self.message = message

        self.background = graphics.create_rect_sprite(rect.Rect((0, 0), (1280, 160)), (70, 80, 65, 200))
        self.text_layout = text.new(FONT, text=message, width=1180, height=180)
        self.text_layout.x = 50
        self.text_layout.y = 20

    def show(self):
        self.game.text_box = self
        # TODO: update key.py etc to pass input only to game.text_box if game.text_box is not None
        pass

    def hide(self):
        self.game.text_box = None

        if self.on_complete_fun is not None:
            self.on_complete_fun()

    def draw(self):
        self.game.screen_objects_to_draw.append(self.background)
        self.game.screen_objects_to_draw.append(self.text_layout)

    def update(self):
        pass
