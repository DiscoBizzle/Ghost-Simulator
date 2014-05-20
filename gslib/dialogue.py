from __future__ import absolute_import, division, print_function

import collections
import io
import os

import pyglet.window.key as Pkey

from gslib.constants import *
from gslib.engine import text, primitives


class Error(Exception):
    pass


class DialoguePlayer(object):

    def __init__(self, game, dialogue_, from_heading, done_func):
        self.game = game
        self.dialogue = dialogue_
        self.heading = from_heading
        self.lines = dialogue_[from_heading][None]
        self.done_func = done_func

        self.choice = None
        self.choice_made = False
        self.done = False

    def play(self):
        self._play_line()

    def _play_choice(self, choice_name):
        self.lines = self.dialogue[self.heading][choice_name]
        self.choice = choice_name
        self.choice_made = True
        self._play_line()

    def _play_line(self):
        if self.done:
            return

        try:
            if len(self.lines) > 0:
                l = self.lines[0]

                if l.startswith('GOTO'):
                    self.heading = l.split(' ', 1)[1]
                    self.lines = self.dialogue[self.heading][None]
                    self.choice_made = False
                    self._play_line()  # go again
                elif l.startswith('PLAY'):
                    self.game.map.active_cutscene = self.game.map.cutscenes[l.split(' ', num=1)[1]]
                    self.game.map.active_cutscene.restart()
                elif l.startswith('DROP') or l.startswith('SUB'):
                    self.choice_made = False
                    self.lines = []

                    if l.startswith('SUB'):
                        found = False
                        found_choice = None

                        # find next choice iff it started with >1 asterisk
                        for y in self.dialogue[self.heading]:
                            if not found:
                                if y == self.choice:
                                    found = True
                            elif y.startswith('*'):
                                found_choice = y
                                break

                        # found choice to substitute in?
                        if found_choice is not None:
                            self.dialogue[self.heading] = collections.OrderedDict(
                                ((k.split(' ', 1)[1], v) if k == found_choice else (k, v))
                                for k, v in self.dialogue[self.heading].iteritems())

                    del self.dialogue[self.heading][self.choice]

                    self._play_line()
                elif l.startswith('END'):
                    self.done_func()
                    self.done = True
                else:
                    # simple dialogue!
                    SimpleDialogue(self.game, l, self._play_line).show()

                self.lines = self.lines[1:]

            elif len(self.dialogue[self.heading].keys()) > 1:
                # choice time!
                hk = filter(lambda x: x is not None and not x.startswith('*'), self.dialogue[self.heading].keys())
                ChoiceDialogue(self.game, hk, self._play_choice).show()

            else:
                self.done_func()
                self.done = True

        except Exception as e:
            raise Error(str(e))


def load_dialogue(filename):
    d = collections.OrderedDict({"# None": []})

    # First pass - organize lines by heading
    with io.open(os.path.join(DIALOGUE_DIR, filename), 'rt', encoding='utf-8') as f:
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
                if not (fword[-1:] == ':' or fword == 'GOTO' or fword == 'PLAY' or fword == 'DROP' or fword == 'SUB'
                        or fword == 'END' or fword.startswith('*')):
                    raise Exception("Syntax error in dialogue file " + filename + ": expected '# some heading' " +
                                    "or '* some choice' or 'somename: blahblah' or 'PLAY d_cutscene_00' or " +
                                    "'GOTO ## some heading', but got '" + l + "'.")

                # Line's okay? Good.
                d[last_heading].append(l)

    # Second pass - find & collate dialogue branches.
    d2 = collections.OrderedDict()
    for heading, lines in d.iteritems():
        new_lines = collections.OrderedDict()

        choice_name = None  # Non-choice lines are represented with the None choice.
        choice_lines_so_far = []

        for l in lines:
            # New choice?
            if l.lstrip()[0] == '*':
                # push old choice
                new_lines[choice_name] = choice_lines_so_far
                # switch to new choice
                choice_name = l.lstrip()[1:].lstrip()
                choice_lines_so_far = []
            else:
                choice_lines_so_far.append(l.lstrip())

        # add the last one (as long as the whole thing wasn't empty!)
        if choice_name is not None or len(choice_lines_so_far) > 0:
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

        self.background = primitives.RectPrimitive(x=0, y=0, width=1280, height=200, color=(70, 80, 65, 200))

        self.text_layout = None
        self._update_text()

        self.wait_up = False

    def _update_text(self):
        self.text_layout = text.new(FONT, font_size=26, text=self.message, width=1180, height=175)
        self.text_layout.content_valign = 'top'
        self.text_layout.x = 50
        self.text_layout.y = 0

    def show(self):
        self.game.dialogue = self
        # TODO: update key.py etc to pass input only to game.dialogue if game.dialogue is not None
        pass

    def hide(self):
        self.game.dialogue = None

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


class ChoiceDialogue(SimpleDialogue):

    def __init__(self, g, choices, o_c_f):
        super(ChoiceDialogue, self).__init__(g, '> ' + '\n'.join(choices), None)

        self.choices = choices
        self.on_complete_choice_fun = o_c_f
        self.wait_prev_repeat = 0
        self.wait_next_repeat = 0
        self.selected = 0

    def hide(self):
        super(ChoiceDialogue, self).hide()

        if self.on_complete_choice_fun is not None:
            self.on_complete_choice_fun(self.choices[self.selected])

    def update(self):
        super(ChoiceDialogue, self).update()

        last_selected = self.selected

        if self.game.key_controller.keys[Pkey.UP]:
            if self.wait_prev_repeat == 0 or (self.wait_prev_repeat >= 10 and self.wait_prev_repeat % 5 == 0):
                self.selected -= 1
            self.wait_prev_repeat += 1
        else:
            self.wait_prev_repeat = 0

        if self.game.key_controller.keys[Pkey.DOWN]:
            if self.wait_next_repeat == 0 or (self.wait_next_repeat >= 10 and self.wait_next_repeat % 5 == 0):
                self.selected += 1
            self.wait_next_repeat += 1
        else:
            self.wait_next_repeat = 0

        self.selected = min(len(self.choices) - 1, max(0, self.selected))

        if last_selected != self.selected:
            cc = self.choices[:]
            cc[self.selected] = '> ' + cc[self.selected]
            self.message = '\n'.join(cc)
            self._update_text()
