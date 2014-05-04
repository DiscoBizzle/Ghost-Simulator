import pyglet.text

from gslib import button


class MessageBox(object):

    def __init__(self, game, text, on_hide_fun=None):
        self.game = game
        self.on_hide_fun = on_hide_fun
        self.background = button.DefaultButton(self, None, (300, 200), text=text, size=(500, 400))
        self.buttons = [self.background]
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
        self.game.screen_objects_to_draw += self.buttons

    def update(self):
        pass


class InfoBox(MessageBox):

    def __init__(self, game, text, on_hide_fun=None):
        MessageBox.__init__(self, game, text, on_hide_fun)
        self.ok_button = button.DefaultButton(self, self.hide, (500, 220), text="OK", size=(100, 60))
        self.buttons.append(self.ok_button)


class QuestionBox(MessageBox):

    def __init__(self, game, text, on_complete_fun=None, on_yes_fun=None, on_no_fun=None):
        MessageBox.__init__(self, game, text, None)
        self.yes_button = button.DefaultButton(self, self.hide, (350, 220), text="Yes", size=(100, 60))
        self.no_button = button.DefaultButton(self, self.hide, (550, 220), text="No", size=(100, 60))
        self.buttons += [self.yes_button, self.no_button]
        self.on_complete_fun = on_complete_fun
        self.on_yes_fun = on_yes_fun
        self.on_no_fun = on_no_fun

    def yes(self):
        self.hide()
        if self.on_yes_fun is not None:
            self.on_yes_fun()
        if self.on_complete_fun is not None:
            self.on_complete_fun(True)

    def no(self):
        self.hide()
        if self.on_no_fun is not None:
            self.on_no_fun()
        if self.on_complete_fun is not None:
            self.on_complete_fun(False)

    def hide(self):
        MessageBox.hide(self)


class InputBox(InfoBox):

    def __init__(self, game, text, start_input, on_finish_input_fun=None):
        InfoBox.__init__(self, game, text, None)
        self.on_finish_input_fin = on_finish_input_fun

        self.input = start_input
        self.text_document = pyglet.text.document.FormattedDocument()
        self.text_document.text = self.input
        self.text_layout = pyglet.text.layout.IncrementalTextLayout(self.text_document, 300, 50, multiline=False)
        self.text_layout.x = 400
        self.text_layout.y = 310
        self.text_caret = pyglet.text.caret.Caret(self.text_layout)
        self.text_caret.select_paragraph(0, 0)

    def show(self):
        InfoBox.show(self)
        self.game.text_caret = self.text_caret

    def hide(self):
        InfoBox.hide(self)
        self.game.text_caret = None
        if self.on_finish_input_fin is not None:
            self.on_finish_input_fin(self.input)

    def draw(self):
        InfoBox.draw(self)
        self.game.screen_objects_to_draw.append(self.text_layout)

    def update(self):
        self.input = self.text_document.text