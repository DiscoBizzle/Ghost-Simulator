import collections

from gslib import button
from gslib import drop_down_list
from gslib import cutscene
from gslib import list_box


class CutsceneEditor(object):
    def __init__(self, game):
        self.game = game

        self.cutscenes = self.game.map.cutscenes.copy()
        self.cutscenes['New... (TODO)'] = None
        self.possible_cutscene_actions = cutscene.possible_actions

        self.static_buttons = []
        self.static_lists = []

        def pu(tine):
            if isinstance(tine, button.Button):
                self.static_buttons.append(tine)
            else:
                self.static_lists.append(tine)
            return tine

        # Misc
        self.toggle_button = pu(button.DefaultButton(self, self.toggle_visible, pos=(0, self.game.dimensions[1] - 20),
                                                     size=(100, 20), text="Cutscenes"))
        self.cutscene_list = pu(drop_down_list.DropDownList(self, self.cutscenes, self.select_cutscene,
                                                            pos=(980, self.game.dimensions[1] - 55),
                                                            size=(300, 20)))
        self.cutscene_status_button = pu(button.DefaultButton(self, None, pos=(1060, self.game.dimensions[1] - 75),
                                         size=(1280 - 1060, 20), text="No cutscene selected."))

        # Cutscene playback controls
        pu(button.DefaultButton(self, self.play_cutscene,
                                pos=(980, self.game.dimensions[1] - 75), size=(20, 20),
                                text=u"\u25B6"))
        pu(button.DefaultButton(self, self.play_cutscene_and_run,
                                pos=(1000, self.game.dimensions[1] - 75),
                                size=(40, 20), text=u"\u25B6 R"))
        pu(button.DefaultButton(self, self.stop_cutscene,
                                pos=(1040, self.game.dimensions[1] - 75), size=(20, 20),
                                text=u"\u25A0"))

        # Controls to add new action
        self.cutscene_new_action_list = pu(drop_down_list.DropDownList(self, cutscene.possible_actions, None,
                                           pos=(980, self.game.dimensions[1] - 95),
                                           size=(280, 20)))
        pu(button.DefaultButton(self, self.add_cutscene_action,
                                pos=(980 + 280, self.game.dimensions[1] - 95),
                                size=(20, 20), text="+"))

        # Manipulate action order
        pu(button.DefaultButton(self, self.push_cutscene_action_up,
                                pos=(880, self.game.dimensions[1] - 115),
                                size=(50, 20), text="push ^"))
        pu(button.DefaultButton(self, self.push_cutscene_action_down,
                                pos=(880, self.game.dimensions[1] - 135),
                                size=(50, 20), text="push v"))
        pu(button.DefaultButton(self, self.delete_cutscene_action,
                                pos=(880, self.game.dimensions[1] - 155),
                                size=(50, 20), text="-"))
        pu(button.DefaultButton(self, self.scroll_cutscene_actions_up,
                                pos=(880, self.game.dimensions[1] - 175),
                                size=(50, 20), text="more ^"))
        pu(button.DefaultButton(self, self.scroll_cutscene_actions_down,
                                pos=(880, self.game.dimensions[1] - 195),
                                size=(50, 20), text="more v"))

        self.selected_cutscene = None
        self.selected_cutscene_action = None
        self.cutscene_actions_desc = collections.OrderedDict()

        self.cutscene_actions_list = pu(list_box.List(self, self.cutscene_actions_desc, self.select_cutscene_action,
                                                      pos=(930, self.game.dimensions[1] - 95), size=(350, 20)))

        self.dyn_buttons = []
        self.dyn_lists = []

        # hide by default
        #self.toggle_visible()

    def _get_buttons(self):
        return self.static_buttons + self.dyn_buttons

    def _get_lists(self):
        return self.static_lists + self.dyn_lists

    buttons = property(_get_buttons)
    lists = property(_get_lists)

    def toggle_visible(self):
        for ce in self.static_buttons + self.static_lists + self.dyn_buttons + self.dyn_lists:
            if ce != self.toggle_button:
                ce.visible = not ce.visible
                ce.enabled = not ce.enabled

    def select_cutscene(self):
        self.selected_cutscene = self.cutscene_list.selected

        if not self.selected_cutscene:
            print('TODO: select new cutscene')

        self.refresh_cutscene_actions()
        self.refresh_cutscene_status()
        # ugh
        self.cutscene_list.selected = None
        self.select_cutscene_action()

    def refresh_cutscene_actions(self):
        self.cutscene_actions_desc.clear()
        if self.selected_cutscene:
            for i in range(0, len(self.selected_cutscene.actions)):
                ca = self.selected_cutscene.actions[i]
                self.cutscene_actions_desc[str(i) + " " + ca.describe()] = ca
        else:
            self.cutscene_actions_desc = {}

        self.cutscene_list.refresh()

        self.select_cutscene_action()

    def refresh_cutscene_status(self):
        if self.selected_cutscene:
            self.cutscene_status_button.text = self.selected_cutscene.name + ": Tick " + str(self.selected_cutscene.tick)
        else:
            self.cutscene_status_button.text = "No cutscene selected."

    def select_cutscene_action(self):
        # remove old shite
        if len(self.dyn_lists) > 0 or len(self.dyn_buttons) > 0:
            self.dyn_lists = []
            self.dyn_buttons = []

        self.selected_cutscene_action = self.cutscene_actions_list.selected

        def add_control(x):
            # ALL the boilerplate!
            if isinstance(x, drop_down_list.DropDownList) or isinstance(x, list_box.List):
                self.dyn_lists.append(x)
            elif isinstance(x, button.Button):
                self.dyn_buttons.append(x)
            add_control.control_i += 1
            x.priority = True

        add_control.control_i = 0

        def wait_group_dec_fun(ev, attr):
            wg = getattr(ev, attr)
            if wg is not None:
                if wg == 1:
                    wg = None
                else:
                    wg -= 1
            setattr(ev, attr, wg)

        def wait_group_inc_fun(ev, attr):
            wg = getattr(ev, attr)
            if wg is None:
                wg = 1
            elif wg == 0:
                pass
            else:
                wg += 1
            setattr(ev, attr, wg)

        def incredifun(thing, attr, fun):
            def clicky():
                fun(thing, attr)
                self.select_cutscene_action()    # re-render controls
                self.refresh_cutscene_actions()  # re-render action descriptions
            return clicky

        # new shite?
        if self.selected_cutscene_action:
            print('ACTUALLY')
            ev = self.selected_cutscene_action

            def get_pos(add_x=20):
                get_pos.x_pos += add_x
                return 930 + get_pos.x_pos - add_x, 240 - get_pos.row * 20

            get_pos.row = 0
            get_pos.x_pos = 0

            container = button.DefaultButton(self, None, pos=(930, 160), size=(1280 - 930, 100))
            add_control(container)
            container.priority = False

            for k, v in ev.get_editor().iteritems():
                add_control(button.DefaultButton(self, None, get_pos(add_x=80), text=k, size=(80, 20)))
                if v == 'wait_group':
                    add_control(button.DefaultButton(self, incredifun(ev, k, wait_group_dec_fun),
                                                     get_pos(), text="-", size=(20, 20)))
                    add_control(button.DefaultButton(self, None, get_pos(add_x=50), text=str(getattr(ev, k)),
                                                     size=(50, 20)))
                    add_control(button.DefaultButton(self, incredifun(ev, k, wait_group_inc_fun),
                                                     get_pos(), text="+", size=(20, 20)))
                elif v == 'int':
                    print('TODO int')
                elif v == 'string':
                    print('TODO string')
                elif v == 'coords':
                    print('TODO coords')
                elif v == 'obj_ref':
                    print('TODO obj_ref')
                else:
                    print("!!! Cutscene action editor doesn't know what a '" + v + "' is")

                get_pos.x_pos = 0
                get_pos.row += 1

    def push_cutscene_action_up(self):
        if self.selected_cutscene and self.selected_cutscene_action:
            i = self.selected_cutscene.actions.index(self.selected_cutscene_action)
            if i > 0:
                self.selected_cutscene.actions.remove(self.selected_cutscene_action)
                self.selected_cutscene.actions.insert(i - 1, self.selected_cutscene_action)
                self.refresh_cutscene_actions()

                # re-select
                self.cutscene_actions_list.selected = self.selected_cutscene_action
                self.select_cutscene_action()

    def push_cutscene_action_down(self):
        if self.selected_cutscene and self.selected_cutscene_action:
            i = self.selected_cutscene.actions.index(self.selected_cutscene_action)
            if i < len(self.selected_cutscene.actions) - 1:
                self.selected_cutscene.actions.remove(self.selected_cutscene_action)
                self.selected_cutscene.actions.insert(i + 1, self.selected_cutscene_action)
                self.refresh_cutscene_actions()

                # re-select
                self.cutscene_actions_list.selected = self.selected_cutscene_action
                self.select_cutscene_action()

    def delete_cutscene_action(self):
        if self.selected_cutscene and self.selected_cutscene_action:
            # delete selected action
            i = self.selected_cutscene.actions.index(self.selected_cutscene_action)
            self.selected_cutscene.actions.remove(self.selected_cutscene_action)
            #del self.selected_cutscene_action
            self.selected_cutscene_action = None

            # update actions list
            self.refresh_cutscene_actions()

            # select something useful
            if len(self.selected_cutscene.actions) > i:
                self.cutscene_actions_list = self.selected_cutscene.actions[i]
            elif len(self.selected_cutscene.actions) > 0:
                self.cutscene_actions_list = self.selected_cutscene.actions[len(self.selected_cutscene.actions) - 1]
            else:
                self.cutscene_actions_list = None

            # update selected action editor
            self.select_cutscene_action()

    def scroll_cutscene_actions_up(self):
        pass

    def scroll_cutscene_actions_down(self):
        pass

    def play_cutscene(self):
        pass

    def play_cutscene_and_run(self):
        pass

    def stop_cutscene(self):
        pass

    def add_cutscene_action(self):
        cnal = self.cutscene_new_action_list
        if self.selected_cutscene and cnal.selected:
            if self.selected_cutscene_action:
                i = self.selected_cutscene.actions.index(self.selected_cutscene_action) + 1
            else:
                i = len(self.selected_cutscene.actions)
            action = cnal.selected(self.game, self.game.map, {})
            self.selected_cutscene.actions.insert(i, action)
            self.refresh_cutscene_actions()
            self.cutscene_actions_list.selected = action
            self.select_cutscene_action()
