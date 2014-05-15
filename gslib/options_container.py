from __future__ import absolute_import, division, print_function

import ast
import errno
import io

import pyglet

from gslib.constants import *


class Options(dict, pyglet.event.EventDispatcher):

    def __setitem__(self, key, value):
        old_value = self.get(key, None)
        #print("option set: {} {} {}".format(key, old_value, value))
        super(Options, self).__setitem__(key, value)
        if value != old_value:
            self.dispatch_event('on_option_change', key, old_value, value)

    def save_options(self):
        try:
            with io.open(OPTIONS_FILE, 'wt', encoding='utf-8') as f:
                for option, val in self.iteritems():
                    f.write(u"{}={}\n".format(option, repr(val)))
        except IOError as e:
            #TODO: proper error handling
            raise

    def load_options(self):
        try:
            with io.open(OPTIONS_FILE, 'rt', encoding='utf-8') as f:
                for l in f:
                    try:
                        if '=' not in l:
                            raise ValueError()
                        option, val = l.split('=', 1)
                        option = option.strip()
                        val = val.strip()
                        if len(option) == 0 or len(val) == 0:
                            raise ValueError()

                        val = ast.literal_eval(val)
                    except ValueError:
                        print("ignoring invalid option: \"{}\"".format(l.strip()))
                        continue
                    # TODO: more sanity checking
                    self[option] = val

        except IOError as e:
            if e.errno == errno.ENOENT:
                # if not found just do nothing
                return
            # TODO: proper error handling
            raise

Options.register_event_type('on_option_change')
