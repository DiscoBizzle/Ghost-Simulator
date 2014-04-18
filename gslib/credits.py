import collections

import pyglet

from gslib.constants import *


def parse_credits_file(fname):
    """Build up a credits dictionary from a text file.

    The items in a credits dictionary are of the form 'job': ['person1', 'person2'].
    The text file format has one item per line, with the job separated
    from a comma-separated list of people by a colon.
    """
    res = collections.defaultdict(list)
    with open(fname) as f:
        for line in f:
            key, names = line.split(":", 1)
            names = [n.strip().decode('utf-8') for n in names.split(",")]
            res[key.decode('utf-8')].extend(names)
    return res


class Credits(object):
    def __init__(self, game, color=(255, 255, 255, 255), size=20, speed=3):
        """Display a credits screen for game.

        Arguments:
            - game: the game whose surface to write to
            - color: colour of the job titles and names
            - size: the text size
            - speed: number of pixels it moves up every game tick
        """
        self.credits = parse_credits_file(CREDITS_FILE)
        self.game = game
        self.color = color
        self.font_size = size
        self.speed = speed
        self.v_offset = 0
        self.batch = pyglet.graphics.Batch()

        text = u""
        for job, names in self.credits.iteritems():
            text += job + '\n'
            for name in names:
                text += '\t' + name + '\n'
            text += '\n'

        self.text_label = pyglet.text.Label(text, FONT, self.font_size, color=self.color,
                                            width=self.game.dimensions[0], batch=self.batch, multiline=True)

    def display(self):
        self.batch.draw()

    def update(self, dt):
        self.text_label.x = (self.game.dimensions[0] - self.text_label.content_width) / 2
        self.text_label.y = self.v_offset
        self.v_offset += self.speed
        if self.v_offset > self.text_label.content_height + self.game.dimensions[1]:
            self.game.set_state(MAIN_MENU)
            self.v_offset = 0
