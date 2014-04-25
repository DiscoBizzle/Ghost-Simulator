import errno

import pyglet

from gslib.constants import *


class Options(dict, pyglet.event.EventDispatcher):
    def __init__(self, *args, **kwargs):
        super(Options, self).__init__(*args, **kwargs)
        self.register_event_type('on_option_change')
        self.load_options()

    def __setitem__(self, k, new_value):
        old_value = self[k] if k in self else None
        #print("option set: {} {} {}".format(k, old_value, new_value))
        super(Options, self).__setitem__(k, new_value)
        if new_value != old_value:
            self.dispatch_event('on_option_change', k, old_value, new_value)

    def save_options(self):
        f = open(OPTIONS_FILE, 'w')
        for option, val in self.iteritems():
            f.write(option + ';' + str(val) + '~' + str(type(val)) + '\n')
        f.close()

    def load_options(self):
        try:
            f = open(OPTIONS_FILE, 'r')
            for l in f:
                semi = l.find(';')
                tilde = l.find('~')
                option = l[:semi]
                val = l[semi+1:tilde]
                typ = l[tilde+1:]
                typ = typ.rstrip()
                if typ == "<type 'bool'>":
                    if val == 'True':
                        val = True
                    else:
                        val = False
                elif typ == "<type 'int'>":
                    val = int(val)
                elif typ == "<type 'float'>":
                    val = float(val)
                elif typ == "<type 'tuple'>":
                    val = val[1:-1].split(', ')
                    val = (int(val[0]), int(val[1]))

                self[option] = val
                self.dispatch_event('on_option_change', option, self[option], val)
            f.close()
        except IOError as e:
            if e.errno == errno.ENOENT:
                # if not found just do nothing
                return
            # TODO proper error handling
            raise
