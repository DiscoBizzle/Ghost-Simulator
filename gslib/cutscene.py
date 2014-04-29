
possible_actions = {}


class CutsceneAction(object):

    def __init__(self, game_, wait_group=None):
        self.game = game_
        self.wait_group = wait_group

    # Used in editor.
    def describe(self):
        return self.__class__.__name__ + " describe() not implemented"

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

    def __init__(self, name, game_, actions):
        self.game = game_
        self.name = name
        self.actions = actions
        self.current_actions = []
        self.remaining_actions = actions.copy()
        self.tick = 0           # just for tracking ticks done
        self.done = False       # just for tracking if finished
        self.wait_group = None  # just for tracking current wait group

    def restart(self):
        self.current_actions = []
        self.remaining_actions = self.actions.copy()
        self.tick = 0           # just for tracking ticks done
        self.done = False       # just for tracking if finished
        self.wait_group = None  # just for tracking current wait group

    def update(self):
        # what is the current wait group?
        last_wait_group = None
        for lwca in self.current_actions:
            if lwca.wait_group is not None:
                last_wait_group = lwca.wait_group
                break

        # any actions eligible to become current?
        while len(self.remaining_actions) > 0:
            ra = self.remaining_actions[0]
            if ra.wait_group == last_wait_group or last_wait_group is None:
                self.current_actions.append(ra)
                self.remaining_actions.remove(ra)
                last_wait_group = ra.wait_group
                ra.restart()
            else:
                break

        # do current actions
        keep_actions = []
        for ca in self.current_actions:
            ca.update()
            if ca.update_again():
                keep_actions.append(ca)
        self.current_actions = keep_actions

        # update stats
        if len(self.current_actions) == 0 and len(self.remaining_actions) == 0:
            self.done = True
        self.wait_group = last_wait_group
        self.tick += 1
