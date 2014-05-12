from gslib import button
from gslib import drop_down_list
from gslib import rect
from gslib import trigger_functions
import json


object_interaction_types = {'Have Fear Harvested': 'harvested_function',
                            'Become Scared': 'feared_function',
                            'Become Possessed': 'possessed_function',
                            'Become Un-Possessed': 'unpossessed_function',
                            'Is Touched': 'is_touched_function',
                            'Is Un-Touched': 'is_untouched_function',
                            'Has Touched': 'has_touched_function',
                            'Has Un-Touched': 'has_untouched_function'}


# get all functions from trigger_functions module
trigger_functions_dict = {}
for i, s in enumerate(dir(trigger_functions)):
    f = getattr(trigger_functions, s)
    if hasattr(f, '__call__'): # check if it is a function
        trigger_functions_dict[unicode(s)] = f  # fill temp dict with 'function_name': function

# decorator to make a called function conditional
def conditional_action(desired_interacters):
    def check_interacter(func):
        def new_func(interactee, interacter):
            if interacter in desired_interacters or len(desired_interacters) == 0:
                func(interactee, interacter)
        new_func.func_name = func.func_name
        return new_func
    return check_interacter


def highlight_button(b, up):
    low = (120, 0, 0)
    low_border = (120, 50, 80)
    high = (0, 120, 0)
    high_border = (0, 200, 0)

    if up:
        b.color = high
        b.border_color = high_border
    else:
        b.color = low
        b.border_color = low_border

class Trigger(object):
    def __init__(self, game, object_refs=None, actions=None, zones=None, interaction_type=None):
        self.game = game
        self.interaction_type = interaction_type

        if object_refs is None:
            self.object_references = {'targets': [], 'conditionals': [], 'interactees': []}
        else:
            self.object_references = object_refs

        if zones is None:
            self.zones = []
        else:
            self.zones = zones

        self.actions = []
        if not actions is None:
            for a in actions:
                self.add_action(a)

    def add_action(self, action):
        if action is None:
            return
        target_objects = [self.game.objects[o_name] for o_name in self.object_references['targets']]
        conditional_objects = [self.game.objects[o_name] for o_name in self.object_references['conditionals']]

        act = action(target_objects)
        cond_act = conditional_action(conditional_objects)(act)
        self.actions.append(cond_act)

    def delete_action(self, action):
        self.actions.remove(action)

    def perf_actions(self, interactee, interacter): # called when triggered NOT by a zone
        for a in self.actions:
            a(interactee, interacter)

    def add_zone(self, zone):
        self.zones.append(zone)

    def delete_zone(self, zone):
        self.zones.remove(zone)

    def check_zone_entry(self, interacter, prev_pos):
        pos = interacter.coord
        for z in self.zones:
            if z.collidepoint(pos) and not z.collidepoint(prev_pos):
                for a in self.actions:
                    a(None, interacter) # no interactee exists
                return True
        return False

    def add_target(self, target):
        self.object_references['targets'].append(target)

    def delete_target(self, target):
        self.object_references['targets'].remove(target)

    def add_conditional(self, cond):
        self.object_references['conditionals'].append(cond)

    def delete_conditional(self, cond):
        self.object_references['conditionals'].remove(cond)

    def add_interactee(self, interactee):
        self.object_references['interactees'].append(interactee)
        self.enable_for_objects()

    def set_interaction_type(self, typ):
        self.interaction_type = typ
        self.enable_for_objects()

    def enable_for_objects(self):
        interactees = [self.game.objects[i] for i in self.object_references['interactees']]
        for interactee in interactees:
            if not self.interaction_type is None:
                def perf_actions_interactee(interacter):
                    return self.perf_actions(interactee, interacter)

                attr = getattr(interactee, self.interaction_type)
                attr.append(perf_actions_interactee)

    def create_save_dict(self):
        save_dict = {}
        save_dict[u'object_references'] = self.object_references

        act_list = [f.__name__ for f in self.actions]
        save_dict[u'actions'] = json.dumps(act_list)

        save_dict[u'interaction_type'] = self.interaction_type

        zones = [json.dumps(z.to_tuple()) for z in self.zones]
        save_dict[u'zones'] = zones

        return save_dict

    def load_from_dict(self, d):
        self.object_references = d[u'object_references']

        self.interaction_type = d[u'interaction_type']

        zones = []
        for tup_string in d[u'zones']: # expected format is json((x, y), (w, h))
            tup = json.loads(tup_string)
            z = rect.Rect(tup[0], tup[1])
            zones.append(z)

        self.zones = zones

        actions = json.loads(d[u'actions'])
        action_funcs = [trigger_functions_dict[a] for a in actions]
        for a in action_funcs:
            self.add_action(a)

        self.enable_for_objects()

    def __del__(self):

        # interactees = [self.game.objects[i] for i in self.object_references['interactees']]
        for interactee in self.object_references['interactees']:
            interactee_obj = self.game.objects[interactee]
            o_funcs = getattr(interactee_obj, self.interaction_type)
            # o_funcs.remove(self.perf_actions)
            for fun in o_funcs:
                if fun.func_name == 'perf_actions_interactee':
                    o_funcs.remove(fun)
                    return


class TriggerEditor(object):
    def __init__(self, game):
        self.game = game

        self.buttons = {}
        self.drop_lists = {}

        self.trigger_to_edit = None
        self.display_zones = []
        self.display_circles = []

        self._pos = (0, 0)
        self.pos = (400, self.game.dimensions[1] - 300)

        self.enabled = False

        self.create_elements()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        self._pos = p
        self.update_element_positions()

    def toggle_self(self, value=None):
        if value is None:
            self.enabled = not self.enabled
        else:
            self.enabled = value
        for k, v in self.buttons.iteritems():
            if not k == 'toggle_trigger_editor':
                v.visible = self.enabled
                v.enabled = self.enabled

        for v in self.drop_lists.itervalues():
            v.visible = self.enabled
            v.enabled = self.enabled

    def update_element_positions(self):
        size = (120, 20)
        vert_spacing = 5
        horizontal_spacing = 5
        p1 = self.pos[1] - size[1] # pos of TriggerEditor is then top-left of first button
        for b in self.buttons.itervalues():
            if b.text == "Trigger Editor":
                continue
            pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
            b.pos = pos
            b.size = size

        for b in self.drop_lists.itervalues():
            pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
            b.pos = pos
            b.size = size

    def create_elements(self):
        self.buttons = {}
        self.drop_lists = {}

        self.buttons['toggle_trigger_editor'] = button.DefaultButton(self, self.toggle_self, text="Trigger Editor", pos=(0, self.game.dimensions[1] - 40))

        db = button.DefaultButton

        dl = drop_down_list.DropDownList

        dls = drop_down_list.DropDownListSlider

        self.buttons['create_new_trigger'] = db(self, self.create_new_trigger, text="New Trigger", order=(0, 0))
        self.drop_lists['triggers'] = dls(self, self.game.map.triggers, self.select_trigger, max_display=4, order=(0, 1))
        self.buttons['delete_trigger'] = db(self, self.delete_selected_trigger, text="Delete Trigger", order=(0, 2))

        self.buttons['interaction_type_label'] = db(self, None, text="Interaction Type", order=(1, 0))
        self.drop_lists['interaction_type'] = dl(self, object_interaction_types, self.set_interaction_type, order=(1, 1))

        self.buttons['pick_interactee'] = db(self, self.pick_interactee, text="Pick Interactee", order=(2, 0))
        self.drop_lists['interactees'] = dl(self, {}, text="<None>", order=(2, 1))

        self.buttons['new_zone'] = db(self, self.create_new_zone, text="New Zone", order=(3, 0))
        self.drop_lists['zones'] = dl(self, {}, self.select_zone, order=(3, 1))

        self.buttons['delete_zone'] = db(self, self.delete_selected_zone, text="Delete Zone", order=(4, 0))
        self.buttons['zone_bottomleft'] = db(self, self.zone_bottomleft, text="Select Bottom Left", order=(4, 1))
        self.buttons['zone_topright'] = db(self, self.zone_topright, text="Select Top Right", order=(4, 2))

        self.buttons['pick_target'] = db(self, self.pick_target, text="Pick Target", order=(5, 0))
        self.drop_lists['targets'] = dl(self, {}, self.delete_target, order=(5, 1))

        self.buttons['pick_conditional'] = db(self, self.pick_conditional, text="Pick Conditional", order=(6, 0))
        self.drop_lists['conditionals'] = dl(self, {}, self.delete_conditional, order=(6, 1))

        self.buttons['action_label'] = db(self, None, text="Action Add/Delete", order=(7, 0))
        self.drop_lists['new_action'] = dl(self, trigger_functions_dict, self.add_action, order=(7, 1))
        self.drop_lists['actions'] = dl(self, {}, self.delete_action, order=(7, 2))

        self.update_element_positions()
        self.toggle_self(False)

    def create_new_trigger(self):
        trig = Trigger(self.game)
        name = 'Trigger 0'
        while True:
            if name in self.game.map.triggers.keys():
                name = name[:name.find(' ') + 1] + str(int(name[name.find(' ') + 1:]) + 1)
            else:
                break
        self.game.map.triggers[name] = trig
        self.drop_lists['triggers'].refresh()
        self.drop_lists['triggers'].set_to_value(name)

    def select_trigger(self):
        trig = self.drop_lists['triggers'].selected
        if trig is None:
            self.drop_lists['zones'].refresh([])
            self.drop_lists['targets'].refresh([])
            self.drop_lists['conditionals'].refresh([])
            self.drop_lists['actions'].refresh([])
            self.drop_lists['interactees'].refresh([])
            return

        self.drop_lists['zones'].refresh(trig.zones)
        self.drop_lists['targets'].refresh(trig.object_references['targets'])
        self.drop_lists['conditionals'].refresh(trig.object_references['conditionals'])
        self.drop_lists['actions'].refresh(trig.actions)
        self.drop_lists['interactees'].refresh(trig.object_references['interactees'])

    def delete_selected_trigger(self):
        trig = self.drop_lists['triggers'].selected
        if trig is None:
            return

        del self.game.map.triggers[self.drop_lists['triggers'].selected_name]
        self.drop_lists['triggers'].selected.__del__()

        self.drop_lists['triggers'].set_to_default()
        self.drop_lists['triggers'].refresh()

    def set_interaction_type(self):
        typ = self.drop_lists['interaction_type'].selected
        trig = self.drop_lists['triggers'].selected
        if trig is None or typ is None:
            return

        trig.set_interaction_type(typ)

    def pick_interactee(self):
        trig = self.drop_lists['triggers'].selected

        if trig is None:
            return

        def choose(o_name):
            trig.add_interactee(o_name)
            self.drop_lists['interactees'].refresh()
            highlight_button(self.buttons['pick_interactee'], False)

        self.game.mouse_controller.pick_object(choose)
        highlight_button(self.buttons['pick_interactee'], True)

    def create_new_zone(self):
        trig = self.drop_lists['triggers'].selected

        if trig is None:
            return

        zone = rect.Rect((0, 0), (1, 1))
        trig.add_zone(zone)

        self.drop_lists['zones'].refresh()
        self.drop_lists['zones'].set_to_value(zone)

    def select_zone(self):
        zone = self.drop_lists['zones'].selected
        if zone is None:
            self.buttons['zone_topright'].enabled = False
            self.buttons['zone_topright'].visible = False
            self.buttons['zone_bottomleft'].enabled = False
            self.buttons['zone_bottomleft'].visible = False
            self.buttons['delete_zone'].enabled = False
            self.buttons['delete_zone'].visible = False
        else:
            self.buttons['zone_topright'].enabled = True
            self.buttons['zone_topright'].visible = True
            self.buttons['zone_bottomleft'].enabled = True
            self.buttons['zone_bottomleft'].visible = True
            self.buttons['delete_zone'].enabled = True
            self.buttons['delete_zone'].visible = True

    def delete_selected_zone(self):
        zone = self.drop_lists['zones'].selected
        trig = self.drop_lists['triggers'].selected
        if zone is None or trig is None:
            return

        trig.delete_zone(zone)

        self.drop_lists['zones'].set_to_default()  # set list to None
        self.drop_lists['zones'].refresh() # update contents of list

    def zone_bottomleft(self):
        zone = self.drop_lists['zones'].selected
        if zone is None:
            return

        def set_bottomleft(pos):
            zone.bottomleft = pos
            self.drop_lists['zones'].refresh()
            self.drop_lists['zones'].set_to_value(zone)
            highlight_button(self.buttons['zone_bottomleft'], False)

        self.game.mouse_controller.pick_position(set_bottomleft)
        highlight_button(self.buttons['zone_bottomleft'], True)

    def zone_topright(self):
        zone = self.drop_lists['zones'].selected
        if zone is None:
            return

        def set_topright(pos):
            w = pos[0] - zone.x
            h = pos[1] - zone.y
            zone.size = (w, h)
            self.drop_lists['zones'].refresh()
            self.drop_lists['zones'].set_to_value(zone)
            highlight_button(self.buttons['zone_topright'], False)

        self.game.mouse_controller.pick_position(set_topright)
        highlight_button(self.buttons['zone_topright'], True)

    def pick_target(self):
        trig = self.drop_lists['triggers'].selected
        if trig is None:
            return

        def choose(target):
            trig.add_target(target)
            self.drop_lists['targets'].refresh() # update contents of list
            highlight_button(self.buttons['pick_target'], False)

        self.game.mouse_controller.pick_object(choose)
        highlight_button(self.buttons['pick_target'], True)

    def delete_target(self):
        target = self.drop_lists['targets'].selected
        trig = self.drop_lists['triggers'].selected
        if trig is None or target is None:
            return

        trig.delete_target(target)

        self.drop_lists['targets'].set_to_default() # set list to None
        self.drop_lists['targets'].refresh() # update contents of list

    def pick_conditional(self):
        trig = self.drop_lists['triggers'].selected

        if trig is None:
            return

        def choose(o_name):
            trig.add_conditional(o_name)
            self.drop_lists['conditionals'].refresh()
            highlight_button(self.buttons['pick_conditional'], False)

        self.game.mouse_controller.pick_object(choose)
        highlight_button(self.buttons['pick_conditional'], True)

    def delete_conditional(self):
        trig = self.drop_lists['triggers'].selected
        cond = self.drop_lists['conditionals'].selected

        if trig is None or cond is None:
            return

        trig.delete_conditional(cond)

        self.drop_lists['conditionals'].refresh()
        self.drop_lists['conditionals'].set_to_default()

    def add_action(self):
        act = self.drop_lists['new_action'].selected
        trig = self.drop_lists['triggers'].selected
        if act is None or trig is None:
            return
        trig.add_action(act)

        self.drop_lists['actions'].refresh()


    def delete_action(self):
        act = self.drop_lists['actions'].selected
        trig = self.drop_lists['triggers'].selected
        if act is None or trig is None:
            return

        trig.delete_action(act)

        self.drop_lists['actions'].refresh()
        self.drop_lists['actions'].set_to_default()


    def display_objects(self, objects):
        pass