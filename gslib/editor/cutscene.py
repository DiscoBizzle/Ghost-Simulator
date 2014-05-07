import collections

from gslib import button
from gslib import cutscene
from gslib import drop_down_list
from gslib import msg_box
from gslib import list_box


class CutsceneEditor(object):
    def __init__(self, game, main_editor):
        self.game = game
        self.main_editor = main_editor

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
        self.play_button = pu(button.DefaultButton(self, self.play_cutscene,
                                                   pos=(980, self.game.dimensions[1] - 75), size=(20, 20),
                                                   text=u"\u25B6"))
        self.play_and_run_button = pu(button.DefaultButton(self, self.play_cutscene_and_run,
                                                           pos=(1000, self.game.dimensions[1] - 75),
                                                           size=(40, 20), text=u"\u25B6 R"))
        self.stop_button = pu(button.DefaultButton(self, self.stop_cutscene,
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

        self.playing = False

        self.highlighted = []

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

    def change_cutscene_action_list_selection(self, action):
        if action is None:
            list_box.list_func(self.cutscene_actions_list, None)()
        else:
            list_box.list_func(self.cutscene_actions_list,
                               str(self.selected_cutscene.actions.index(action)) + " " + action.describe())()

    def select_cutscene(self):
        self.selected_cutscene = self.cutscene_list.selected

        if not self.selected_cutscene:
            mb = msg_box.InputBox(self.game, 'TODO: create new cutscene. (for now, edit .json)', 'hi')
            mb.show()

        self.refresh_cutscene_actions()
        self.refresh_cutscene_status()
        # ugh
        self.change_cutscene_action_list_selection(None)
        self.refresh_cutscene_actions()

        # double ugh
        self.highlighted = []

    def refresh_cutscene_actions(self):
        self.cutscene_actions_desc.clear()
        if self.selected_cutscene:
            for i in range(0, len(self.selected_cutscene.actions)):
                ca = self.selected_cutscene.actions[i]
                self.cutscene_actions_desc[str(i) + " " + ca.describe()] = ca
        else:
            self.cutscene_actions_desc = {}

        self.cutscene_actions_list.refresh()

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

        # changed? upkeep...
        if self.selected_cutscene_action != self.cutscene_actions_list.selected:
            self.highlighted = []

        self.selected_cutscene_action = self.cutscene_actions_list.selected

        def add_control(x):
            # ALL the boilerplate!
            if isinstance(x, drop_down_list.DropDownList) or isinstance(x, list_box.List):
                self.dyn_lists.append(x)
            elif isinstance(x, button.Button):
                self.dyn_buttons.append(x)
            add_control.control_i += 1
            x.priority = True
            return x

        add_control.control_i = 0

        def int_dec_fun(ev, attr):
            setattr(ev, attr, getattr(ev, attr) - 1)

        def int_inc_fun(ev, attr):
            setattr(ev, attr, getattr(ev, attr) + 1)

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

        def obj_ref_sel_fun(ev, attr):
            def finish_obj_click(o_name):
                self.highlighted.remove(str(ev) + '-' + attr)
                setattr(ev, attr, o_name)
                self.select_cutscene_action()
                self.refresh_cutscene_actions()
            # are they actually unclicking the button?
            if (str(ev) + '-' + attr) in self.highlighted:
                self.highlighted.remove(str(ev) + '-' + attr)
            else:
                self.highlighted.append(str(ev) + '-' + attr)
                self.game.mouse_controller.pick_object(finish_obj_click)

        def pick_coords_fun(ev, attr):
            def finish_coords_click(pos):
                self.highlighted.remove(str(ev) + '-' + attr)
                dest = pos
                dest = (dest[0] - 12, dest[1])
                setattr(ev, attr, dest)
                self.select_cutscene_action()
                self.refresh_cutscene_actions()
            # unclicking?
            if (str(ev) + '-' + attr) in self.highlighted:
                self.highlighted.remove(str(ev) + '-' + attr)
            else:
                self.highlighted.append(str(ev) + '-' + attr)
                self.game.mouse_controller.pick_position(finish_coords_click)

        def incredifun(thing, attr, fun):
            def clicky():
                fun(thing, attr)
                self.select_cutscene_action()    # re-render controls
                self.refresh_cutscene_actions()  # re-render action descriptions
            return clicky

        # new shite?
        if self.selected_cutscene_action:
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
                    add_control(button.DefaultButton(self, incredifun(ev, k, int_dec_fun),
                                                     get_pos(), text="-", size=(20, 20)))
                    add_control(button.DefaultButton(self, None, get_pos(add_x=50), text=str(getattr(ev, k)),
                                                     size=(50, 20)))
                    add_control(button.DefaultButton(self, incredifun(ev, k, int_inc_fun),
                                                     get_pos(), text="+", size=(20, 20)))
                elif v == 'string':
                    print('TODO string')
                elif v == 'obj_ref':
                    add_control(button.DefaultButton(self, None, get_pos(add_x=100), text=getattr(ev, k),
                                                     size=(100, 20)))

                    if not (str(ev) + '-' + k) in self.highlighted:
                        add_control(button.DefaultButton(self, incredifun(ev, k, obj_ref_sel_fun), get_pos(50),
                                                         text="Pick", size=(50, 20)))
                    else:
                        add_control(button.Button(self, incredifun(ev, k, obj_ref_sel_fun), get_pos(50), text="Pick",
                                                  size=(50, 20), colour=(0, 120, 0), border_colour=(0, 200, 0),
                                                  border_width=3))
                elif v == 'coords':
                    add_control(button.DefaultButton(self, None, get_pos(add_x=100), text=str(getattr(ev, k)),
                                                     size=(100, 20)))

                    if not (str(ev) + '-' + k) in self.highlighted:
                        add_control(button.DefaultButton(self, incredifun(ev, k, pick_coords_fun), get_pos(50),
                                                         text="Pick", size=(50, 20)))
                    else:
                        add_control(button.Button(self, incredifun(ev, k, pick_coords_fun), get_pos(50), text="Pick",
                                                  size=(50, 20), colour=(0, 120, 0), border_colour=(0, 200, 0),
                                                  border_width=3))
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
                self.change_cutscene_action_list_selection(self.selected_cutscene_action)
                self.select_cutscene_action()

    def push_cutscene_action_down(self):
        if self.selected_cutscene and self.selected_cutscene_action:
            i = self.selected_cutscene.actions.index(self.selected_cutscene_action)
            if i < len(self.selected_cutscene.actions) - 1:
                self.selected_cutscene.actions.remove(self.selected_cutscene_action)
                self.selected_cutscene.actions.insert(i + 1, self.selected_cutscene_action)
                self.refresh_cutscene_actions()

                # re-select
                self.change_cutscene_action_list_selection(self.selected_cutscene_action)
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
                self.change_cutscene_action_list_selection(self.selected_cutscene.actions[i])
            elif len(self.selected_cutscene.actions) > 0:
                self.change_cutscene_action_list_selection(
                    self.selected_cutscene.actions[len(self.selected_cutscene.actions) - 1])
            else:
                self.change_cutscene_action_list_selection(None)

            # update selected action editor
            self.select_cutscene_action()

    def scroll_cutscene_actions_up(self):
        pass

    def scroll_cutscene_actions_down(self):
        pass

    def play_cutscene(self):
        self.play_cutscene_and_run()
        return

    def cutscene_play_exception(self, e):
        self.stop_cutscene()
        mb = msg_box.InfoBox(self.game,
                             """The way is long but you can make it easy on me
                                And the mother we share will never keep your cool code from falling
                                And when it all fucks up, you put your head in my hands
                                And the mother we share will never keep your real funcs from calling~

                                """ + str(e))
        mb.show()

    def play_cutscene_and_run(self):
        if self.selected_cutscene:
            self.game.update_exception_hook = (cutscene.Error, self.cutscene_play_exception)

            # disable main editor controls
            self.main_editor.disable_main_editor()

            # disable (most of) cutscene editor
            for x in self.buttons + self.dyn_buttons + self.lists + self.dyn_lists:
                x.enabled = False
            self.stop_button.enabled = True

            # highlight the only shit that still works
            self.play_and_run_button.colour = (0, 120, 0)
            self.play_and_run_button.border_colour = (0, 200, 0)
            self.stop_button.colour = (120, 120, 0)
            self.stop_button.border_colour = (200, 200, 0)

            # actually start cutscene
            self.main_editor.exit_edit_mode()  # save game state
            self.game.map.active_cutscene = self.selected_cutscene
            self.selected_cutscene.restart()
            self.playing = True

            self.game.force_run_objects = True  # allow main game objects to update

    def stop_cutscene(self):
        if self.playing:
            # unhook exception handler
            self.game.update_exception_hook = (None, None)

            # re-enable main editor controls
            self.main_editor.enable_main_editor()

            # re-enable cutscene editor controls
            for x in self.buttons + self.dyn_buttons + self.lists + self.dyn_lists:
                x.enabled = True

            # restore colour of play controls back to normal
            self.play_button.colour = (120, 0, 0)
            self.play_button.border_colour = (120, 50, 80)
            self.play_and_run_button.colour = (120, 0, 0)
            self.play_and_run_button.border_colour = (120, 50, 80)
            self.stop_button.colour = (120, 0, 0)
            self.stop_button.border_colour = (120, 50, 80)

            # actually stop cutscene
            self.main_editor.enter_edit_mode()  # load game state
            self.game.map.active_cutscene.restart()  # stop embracing like everything
            self.game.map.active_cutscene = None
            self.game.force_run_objects = False
            self.playing = False

    def update(self):
        if self.playing:
            self.refresh_cutscene_status()

            if self.game.map.active_cutscene.done:
                self.stop_cutscene()

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
            self.change_cutscene_action_list_selection(action)
            self.select_cutscene_action()
