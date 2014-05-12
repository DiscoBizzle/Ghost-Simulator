from gslib import dialogue


class Error(Exception):
    """Cutscene exception"""
    pass


class CutsceneAction(object):

    def __init__(self, game_, map_, load_dict=None):
        self.game = game_
        self.map = map_
        self.edit_control_map = {}
        self.to_save = []
        self.load_dict = load_dict or {}
        self.wait_til_done = self.property('wait_til_done', 'bool', default=True)

    def property(self, name, editor_type, default=None):
        self.edit_control_map[name] = editor_type
        self.to_save.append(name)

        if name in self.load_dict:
            return self.load_dict[name]
        else:
            return default

    def get_editor(self):
        return self.edit_control_map

    def save(self):
        d = {'class_name': self.__class__.__name__}
        for k in self.to_save:
            d[k] = getattr(self, k)
        return d

    # Used in editor.
    def describe(self):
        return ("WAIT AFTER " if self.wait_til_done else "") + self.__class__.__name__[:-6] + ": "

    # Called when CutsceneAction should forget its state and start anew.
    def restart(self):
        pass

    # Should update() be called again next tick?
    def update_again(self):
        return False

    # Gets called once per tick at least once and then as long as update_again() returns True.
    def update(self):
        raise Exception("CutsceneAction '" + self.__class__.__name__ + "' update() not implemented!")


class Cutscene(object):

    def __init__(self, name, actions):
        self.name = name
        self.actions = actions
        self.current_actions = []
        self.remaining_actions = actions[:]
        self.tick = 0            # just for tracking ticks done
        self.done = False        # just for tracking if finished
        self.waiting_for = []    # just for tracking current wait group

    def restart(self):
        self.current_actions = []
        self.remaining_actions = self.actions[:]
        self.tick = 0           # just for tracking ticks done
        self.done = False       # just for tracking if finished
        self.waiting_for = []   # just for tracking current wait group

    def update(self):
        # anything currently running & blocking new events?
        wait_for = []
        for ca in self.current_actions:
            if ca.wait_til_done:
                wait_for.append(ca)

        # any actions eligible to become current?
        if len(wait_for) == 0:
            while len(self.remaining_actions) > 0:
                ra = self.remaining_actions[0]
                self.current_actions.append(ra)
                self.remaining_actions.remove(ra)
                ra.restart()
                if ra.wait_til_done and ra.update_again():
                    wait_for.append(ra)
                    break

        # do current actions
        keep_actions = []
        for ca in self.current_actions:
            ca.update()
            if ca.update_again():
                keep_actions.append(ca)
        self.current_actions = keep_actions

        # update stats
        self.done = len(self.current_actions) == 0 and len(self.remaining_actions) == 0
        self.waiting_for = wait_for
        self.tick += 1


class SleepAction(CutsceneAction):

    def __init__(self, g, m, l):
        CutsceneAction.__init__(self, g, m, l)
        self.ticks = self.property('ticks', 'int', default=20)
        self.ticks_remaining = self.ticks

    def describe(self):
        return super(SleepAction, self).describe() + str(self.ticks) + " ticks"

    def restart(self):
        self.ticks_remaining = self.ticks

    def update_again(self):
        return self.ticks_remaining > 0

    def update(self):
        self.ticks_remaining -= 1


class ControllingCutsceneAction(CutsceneAction):

    def __init__(self, g, m, l):
        CutsceneAction.__init__(self, g, m, l)
        self.what = self.property('what', 'obj_ref', default='<None>')

    def valid_ref(self):
        return self.what in self.map.objects

    def get_ref(self):
        return self.map.objects[self.what]

    def hook(self):
        if not self.valid_ref():
            if self.what == '<None>':
                raise Error("Action not configured. You need to set .what on:\n" + self.describe())
            else:
                raise Error("Couldn't find thing named '" + self.what + "' in the current map\n" + self.describe())
        self.get_ref().cutscene_controlling.append(self)

    def unhook(self):
        if self.valid_ref() and self in self.get_ref().cutscene_controlling:
            self.get_ref().cutscene_controlling.remove(self)

    def game_object_hook(self, o):
        pass


class ToggleAIAction(ControllingCutsceneAction):

    def __init__(self, g, m, l, toggle_dir):
        super(ToggleAIAction, self).__init__(g, m, l)
        self.done = False
        self.toggle_dir = toggle_dir

    def describe(self):
        return super(ToggleAIAction, self).describe() + self.what

    def update_again(self):
        return not self.done

    def update(self):
        if not self.done:
            # stand still!
            self.get_ref().velocity = (0, 0)

            # if any player is possessing this, kick 'em out.
            for p in self.game.players:
                if p.possessing == self.get_ref():
                    p.toggle_possess()

            if not self.toggle_dir:
                self.hook()
            else:
                self.get_ref().cutscene_controlling = []
            self.done = True

    def restart(self):
        self.done = False


class DisableAIAction(ToggleAIAction):

    def __init__(self, g, m, l):
        super(DisableAIAction, self).__init__(g, m, l, False)


class EnableAIAction(ToggleAIAction):

    def __init__(self, g, m, l):
        super(EnableAIAction, self).__init__(g, m, l, True)


class WalkToAction(ControllingCutsceneAction):

    def __init__(self, g, m, l):
        ControllingCutsceneAction.__init__(self, g, m, l)
        self.where = self.property('where', 'coords', default=(0, 0))
        self.speed = self.property('speed', 'int', default=2)

    def describe(self):
        return ControllingCutsceneAction.describe(self) + " " + self.what + " -> " + str(self.where) + \
                                                          " x" + str(self.speed)

    def update_again(self):
        return self.valid_ref() and (self.get_ref().coord[0] != self.where[0] or
                                     self.get_ref().coord[1] != self.where[1])

    def update(self):
        self.hook()

    def restart(self):
        self.unhook()

    def game_object_hook(self, ch):
        p_start = ch.coord
        p_end = self.where

        if not self.update_again():
            self.unhook()
        else:
            ch.velocity = (min(self.speed, max(-self.speed, p_end[0] - p_start[0])),
                           min(self.speed, max(-self.speed, p_end[1] - p_start[1])))


class ChangeObjectStateAction(ControllingCutsceneAction):

    def __init__(self, g, m, l):
        super(ChangeObjectStateAction, self).__init__(g, m, l)
        self.state = self.property('state', 'string_drop_down')
        self.done = False

    def describe(self):
        return super(ChangeObjectStateAction, self).describe() + self.what + " -> " + str(self.state)

    def restart(self):
        self.done = False

    def update(self):
        if not self.done:
            self.get_ref().state_index = self.state
            self.done = True

    def update_again(self):
        return not self.done

    def get_autocomplete(self, var):
        if var == 'state':
            return self.get_ref().states.keys()
        else:
            return []


class DialogueAction(CutsceneAction):

    def __init__(self, g, m, l):
        super(DialogueAction, self).__init__(g, m, l)
        self.dialogue_file = self.property('dialogue_file', 'dialogue_file', default=None)
        self.from_heading = self.property('from_heading', 'dialogue_heading', default=None)
        self.player = None
        self.done = False

    def update_again(self):
        return not self.done

    def restart(self):
        self.player = None
        self.done = False

    def _finished(self):
        self.player = None
        self.done = True

    def update(self):
        if self.done:
            return

        if self.player is None:
            if self.dialogue_file is None:
                raise Error("DialogueAction: You must select a dialogue_file.")
            if self.from_heading is None:
                raise Error("DialogueAction: You must select a heading to play from.")

            try:
                self.player = dialogue.DialoguePlayer(self.game, dialogue.load_dialogue(self.dialogue_file),
                                                      self.from_heading, self._finished)
                self.player.play()
            except Exception as e:
                raise Error(str(e))


possible_actions = {'Sleep': SleepAction, 'Walk To': WalkToAction, 'Disable AI': DisableAIAction,
                    'Enable AI': EnableAIAction, 'Dialogue': DialogueAction,
                    'Change Object State': ChangeObjectStateAction}
