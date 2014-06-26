from __future__ import absolute_import, division, print_function

import pyglet.text

from gslib.ui import button
from gslib import window


class MessageBox(pyglet.event.EventDispatcher):

    def __init__(self, game, text, on_hide_fun=None):
        self.game = game
        if on_hide_fun is not None:
            self.on_hide = on_hide_fun
        self.background = button.DefaultButton(owner=self, function=None, pos=(300, 200), text=text, size=(500, 400))
        self.buttons = []
        self.visible = False

    def hide(self):
        self.game.message_box = None
        self.visible = False
        self.background.visible = False
        for b in self.buttons:
            b.visible = False
            b.enabled = False

        self.dispatch_event('on_hide')

    def show(self):
        self.game.message_box = self
        self.visible = True
        self.background.visible = True
        for b in self.buttons:
            b.visible = True
            b.enabled = True

    def draw(self):
        self.background.draw()
        for b in self.buttons:
            b.draw()

    def update(self):
        pass

MessageBox.register_event_type('on_hide')


class InfoBox(MessageBox):

    def __init__(self, game, text, on_hide_fun=None):
        super(InfoBox, self).__init__(game, text, on_hide_fun)
        self.ok_button = button.DefaultButton(owner=self, function=self.hide, pos=(500, 220), text="OK", size=(100, 60))
        self.buttons.append(self.ok_button)


class QuestionBox(MessageBox):

    def __init__(self, game, text, on_complete_fun=None, on_yes_fun=None, on_no_fun=None):
        super(QuestionBox, self).__init__(game, text, None)
        self.yes_button = button.DefaultButton(owner=self, function=self.yes, pos=(350, 220), text="Yes", size=(100, 60))
        self.no_button = button.DefaultButton(owner=self, function=self.no, pos=(550, 220), text="No", size=(100, 60))
        self.buttons.append(self.yes_button)
        self.buttons.append(self.no_button)
        if on_complete_fun is not None:
            self.on_complete = on_complete_fun
        if on_yes_fun is not None:
            self.on_yes = on_yes_fun
        if on_no_fun is not None:
            self.on_no = on_no_fun

    def yes(self):
        self.hide()
        self.dispatch_event('on_yes')
        self.dispatch_event('on_complete')

    def no(self):
        self.hide()
        self.dispatch_event('on_no')
        self.dispatch_event('on_complete')

QuestionBox.register_event_type('on_complete')
QuestionBox.register_event_type('on_yes')
QuestionBox.register_event_type('on_no')


class InputBox(InfoBox):

    def __init__(self, game, text, start_input, on_finish_input_fun=None):
        super(InputBox, self).__init__(game, text, None)
        if on_finish_input_fun is not None:
            self.on_finish_input = on_finish_input_fun

        self.input = start_input
        self.text_document = pyglet.text.document.FormattedDocument()
        self.text_document.text = self.input
        self.text_layout = pyglet.text.layout.IncrementalTextLayout(self.text_document, 300, 50, multiline=False)
        self.text_layout.x = 400
        self.text_layout.y = 310
        self.text_caret = pyglet.text.caret.Caret(self.text_layout)
        self.text_caret.select_paragraph(0, 0)

    def _in_caret_bounds(self, x, y):
        return (self.text_layout.x <= x < self.text_layout.x + self.text_layout.width and
                self.text_layout.y <= y < self.text_layout.y + self.text_layout.height)

    def show(self):
        window.push_handlers(self)
        super(InputBox, self).show()

    def hide(self):
        super(InputBox, self).hide()
        window.remove_handlers(self)
        self.dispatch_event('on_finish_input', self.input)

    def draw(self):
        super(InputBox, self).draw()
        self.text_layout.draw()

    def update(self):
        self.input = self.text_document.text

    def on_activate(self):
        return self.text_caret.on_activate()

    def on_deactivate(self):
        return self.text_caret.on_deactivate()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self._in_caret_bounds(x, y):
            self.text_caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return pyglet.event.EVENT_HANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        if self._in_caret_bounds(x, y):
            self.text_caret.on_mouse_press(x, y, button, modifiers)
        return pyglet.event.EVENT_HANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._in_caret_bounds(x, y):
            self.text_caret.on_mouse_scroll(x, y, scroll_x, scroll_y)
        return pyglet.event.EVENT_HANDLED

    def on_text(self, text):
        return self.text_caret.on_text(text)

    def on_text_motion(self, motion):
        return self.text_caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        return self.text_caret.on_text_motion_select(motion)

    @staticmethod
    def on_key_press(symbol, modifiers):
        return pyglet.event.EVENT_HANDLED

    @staticmethod
    def on_key_release(symbol, modifiers):
        return pyglet.event.EVENT_HANDLED

InputBox.register_event_type('on_finish_input')
