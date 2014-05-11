import collections
import os

import pyglet.window.key as Pkey

from gslib.constants import *
from gslib import graphics
from gslib import rect
from gslib import text


class Error(Exception):
    pass


class DialoguePlayer(object):

    def __init__(self, game, dialogue_, from_heading, done_func):
        self.game = game
        self.dialogue = dialogue_
        self.heading = from_heading
        self.lines = dialogue_[from_heading][None]
        self.done_func = done_func

        self.choice_made = False
        self.done = False

    def play(self):
        self._play_line()

    def _play_choice(self, choice_name):
        self.lines = self.dialogue[self.heading][choice_name]
        self.choice_made = True

    def _play_line(self):
        if self.done:
            return

        try:
            if len(self.lines) > 0:
                l = self.lines[0]

                if l.startswith('GOTO'):
                    self.heading = l.split(' ', num=1)[1]
                    self.lines = self.dialogue[self.heading][None]
                    self.choice_made = False
                elif l.startswith('PLAY'):
                    self.game.map.active_cutscene = self.game.map.cutscenes[l.split(' ', num=1)[1]]
                    self.game.map.active_cutscene.restart()
                else:
                    # simple dialogue!
                    SimpleDialogue(self.game, l, self._play_line).show()

                self.lines = self.lines[1:]

            elif len(self.dialogue[self.heading].keys()) > 1 and not self.choice_made:
                # choice time!
                ChoiceDialogue(self.game, self.dialogue[self.heading].keys(), self._play_choice).show()
                pass

            else:
                self.done_func()
                self.done = True

        except Exception as e:
            raise Error(str(e))


def load_dialogue(filename):
    d = collections.OrderedDict({"# None": []})

    # First pass - organize lines by heading
    with open(os.path.join(DIALOGUE_DIR, filename), 'r') as f:
        lines = f.readlines()

        # filter blank lines
        lines = filter(lambda l: l.lstrip() != "", lines)

        # strip lines that start with '('
        lines = filter(lambda l: l.lstrip()[0] != '(', lines)

        # key lines by preceding heading.
        last_heading = "# None"

        for l in lines:
            l = l.replace('\r', '').replace('\n', '')

            if l.lstrip()[0] == '#':
                if l in d:
                    raise Exception("Duplicate heading '" + l + "' in " + filename)
                d[l] = []
                last_heading = l
            else:
                # Quick syntax check:
                # Remaining lines *must* be 'SomeName: blahablah' or 'GOTO whatever' or 'PLAY c_00' or '* some choice'.
                fword = l.lstrip().split(' ')[0]
                if not (fword[-1:] == ':' or fword == 'GOTO' or fword == 'PLAY' or fword == '*'):
                    raise Exception("Syntax error in dialogue file " + filename + ": expected '# some heading' " +
                                    "or '* some choice' or 'somename: blahblah' or 'PLAY d_cutscene_00' or " +
                                    "'GOTO ## some heading', but got '" + l + "'.")

                # Line's okay? Good.
                d[last_heading].append(l)

    # Second pass - find & collate dialogue branches.
    d2 = collections.OrderedDict()
    for heading, lines in d.iteritems():
        new_lines = {}

        choice_name = None  # Non-choice lines are represented with the None choice.
        choice_lines_so_far = []

        for l in lines:
            # New choice?
            if l.lstrip()[:2] == '* ':
                # push old choice (iff non-empty)
                if len(choice_lines_so_far) > 0:
                    new_lines[choice_name] = choice_lines_so_far
                # switch to new choice
                choice_name = l.lstrip()[2:]
                choice_lines_so_far = []
            else:
                choice_lines_so_far.append(l.lstrip())

        # add the last one (iff non-empty)
        if len(choice_lines_so_far) > 0:
            new_lines[choice_name] = choice_lines_so_far

        # add heading (iff non-empty)
        if len(new_lines.keys()) > 0:
            d2[heading] = new_lines

    return d2


class SimpleDialogue(object):
    def __init__(self, game, message, on_complete_fun):
        self.game = game
        self.on_complete_fun = on_complete_fun
        self.message = message

        self.background = graphics.create_rect_sprite(rect.Rect((0, 0), (1280, 160)), (70, 80, 65, 200))
        self.text_layout = text.new(FONT, font_size=20, text=message, width=1180, height=180)
        self.text_layout.x = 50
        self.text_layout.y = 20

        self.wait_up = False

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
        if self.game.key_controller.keys[Pkey.ENTER]:
            self.wait_up = True
        if self.wait_up and not self.game.key_controller.keys[Pkey.ENTER]:
            self.hide()


# TODO
class ChoiceDialogue(SimpleDialogue):

    def __init__(self, g, choices, o_c_f):
        raise Error("ChoiceDialogue is not implemented yet!")
