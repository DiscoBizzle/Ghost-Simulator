import pyglet.text

from gslib import button
from gslib import key


class MessageBox(object):

    def __init__(self, game, text, on_hide_fun=None):
        self.game = game
        self.on_hide_fun = on_hide_fun

        self.background = button.DefaultButton(self, None, (300, 200), text=text, size=(500, 400))
        self.ok_button = button.DefaultButton(self, self.hide, (500, 220), text="OK", size=(100, 60))

        self.buttons = [self.background, self.ok_button]

        self.visible = False

    def hide(self):
        self.game.message_box = None
        self.visible = False

        if self.on_hide_fun is not None:
            self.on_hide_fun()

    def show(self):
        self.game.message_box = self
        self.visible = True

    def draw(self):
        spr = [self.background.outer_sprite, self.background.inner_sprite, self.background.text_sprite,
               self.ok_button.outer_sprite, self.ok_button.inner_sprite, self.ok_button.text_sprite]
        self.game.screen_objects_to_draw += spr

    def update(self):
        pass


class InputBox(MessageBox):

    def __init__(self, game, text, start_input, on_hide_fun=None):
        MessageBox.__init__(self, game, text, on_hide_fun)

        self.input = start_input
        self.text_document = pyglet.text.document.FormattedDocument()
        self.text_document.text = self.input
        self.text_layout = pyglet.text.layout.IncrementalTextLayout(self.text_document, 300, 50, multiline=False)
        self.text_layout.x = 400
        self.text_layout.y = 310
        self.text_caret = pyglet.text.caret.Caret(self.text_layout)
        self.text_caret.select_paragraph(0, 0)

    def show(self):
        #self.game.push_handlers(self.text_caret)
        self.game.key_controller.on_text_handler = self.text_caret.on_text
        self.game.key_controller.on_text_motion_handler = self.text_caret.on_text_motion
        self.game.key_controller.on_text_motion_select_handler = self.text_caret.on_text_motion_select
        self.game.key_controller.disable_game_keys = True
        MessageBox.show(self)

    def hide(self):
        #self.game.pop_handlers()
        self.game.key_controller.on_text_handler = None
        self.game.key_controller.on_text_motion_handler = None
        self.game.key_controller.on_text_motion_select_handler = None
        self.game.key_controller.disable_game_keys = False
        MessageBox.hide(self)

    def draw(self):
        MessageBox.draw(self)
        self.game.screen_objects_to_draw.append(self.text_layout)

    def update(self):
        self.input = self.text_document.text