from __future__ import absolute_import, division, print_function

import io
import collections

import pyglet

from gslib import window
from gslib.constants import *


def parse_credits_file(fname):
    """Build up a credits dictionary from a text file.

    The items in a credits dictionary are of the form 'job': ['person1', 'person2'].
    The text file format has one item per line, with the job separated
    from a comma-separated list of people by a colon.
    """
    res = collections.defaultdict(list)
    with io.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            key, names = line.split(":", 1)
            names = [n.strip() for n in names.split(",")]
            res[key].extend(names)
    return res


class Credits(pyglet.event.EventDispatcher):
    def __init__(self, color=(255, 255, 255, 255), size=20, speed=1):
        """Display a credits screen for game.

        Arguments:
            - game: the game whose surface to write to
            - color: colour of the job titles and names
            - size: the text size
            - speed: number of pixels it moves up every 1/60 of a second
        """
        self.credits = parse_credits_file(CREDITS_FILE)
        self.color = color
        self.font_size = size
        self.speed = speed
        self.v_offset = 0
        self.batch = pyglet.graphics.Batch()

        items = []
        for job, names in self.credits.iteritems():
            items.append(u'{}\n'.format(job))
            for name in names:
                items.append(u'\t{}\n'.format(name))
            items.append(u'\n')
        text = u''.join(items)

        self.text_label = pyglet.text.Label(text, FONT, self.font_size, color=self.color,
                                            width=window.width, batch=self.batch, multiline=True)

    def on_draw(self):
        window.clear()
        self.batch.draw()

    def update(self, dt):
        self.v_offset += self.speed
        self.text_label.y = self.v_offset
        if self.v_offset > self.text_label.content_height + window.height:
            self.stop()

    def start(self):
        self.on_resize(*window.get_size())
        self.text_label.y = self.v_offset
        pyglet.clock.schedule_interval(self.update, 1 / 60)
        window.push_handlers(self)

    def stop(self):
        self.v_offset = 0
        window.remove_handlers(self)
        pyglet.clock.unschedule(self.update)
        self.dispatch_event('on_credits_end')

    def on_resize(self, width, height):
        self.text_label.x = (width - self.text_label.content_width) // 2

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.stop()
            return pyglet.event.EVENT_HANDLED

Credits.register_event_type('on_credits_end')
