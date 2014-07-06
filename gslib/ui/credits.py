from __future__ import absolute_import, division, print_function

import io

import pyglet
from pyglet.window import key

from gslib.engine.camera import Camera, CameraGroup
from gslib import window
from gslib.constants import *


def parse_credits_file(fname):
    """Build up a credits dictionary from a text file.

    The items in a credits dictionary are of the form 'job': ['person1', 'person2'].
    The text file format has one item per line, with the job separated
    from a comma-separated list of people by a colon.
    """
    res = {}
    with io.open(fname, 'rt', encoding='utf-8') as f:
        for line in f:
            job, names = line.split(":", 1)
            res[job] = [n.strip() for n in names.split(",")]
    return res


class Credits(pyglet.event.EventDispatcher):
    def __init__(self, color=(255, 255, 255, 255), size=20, speed=1):
        """Display a credits screen for game.

        :type color: (int, int, int, int)
        :param color: color of the job titles and names
        :type size: int
        :param size: the text size
        :type speed: int
        :param speed: number of pixels it moves up every 1/60 of a second
        """
        self.credits = parse_credits_file(CREDITS_FILE)
        self.color = color
        self.font_size = size
        self.speed = speed
        self.batch = pyglet.graphics.Batch()
        self.camera = Camera(x=0, y=0, zoom=1.0)
        self.camera_group = CameraGroup(self.camera)

        items = []
        for job, names in self.credits.iteritems():
            items.append(u'{}\n'.format(job))
            for name in names:
                items.append(u'\t{}\n'.format(name))
            items.append(u'\n')
        text = u''.join(items)

        self.text_label = pyglet.text.Label(text=text, font_name=FONT, font_size=self.font_size, color=self.color,
                                            width=window.width, batch=self.batch, group=self.camera_group,
                                            multiline=True)

    def on_draw(self):
        window.clear()
        self.batch.draw()

    def update(self, dt):
        self.camera.y -= self.speed
        if -self.camera.y > self.text_label.content_height + window.height:
            self.stop()

    def start(self):
        self.on_resize(window.width, window.height)
        pyglet.clock.schedule_interval(self.update, 1 / 60)
        window.push_handlers(self)

    def stop(self):
        self.camera.y = 0
        window.remove_handlers(self)
        pyglet.clock.unschedule(self.update)
        self.dispatch_event('on_credits_end')

    def on_resize(self, width, height):
        self.camera.x = -(width - self.text_label.content_width) // 2

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.stop()
            return pyglet.event.EVENT_HANDLED

Credits.register_event_type('on_credits_end')
