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
            if interacter in desired_interacters:
                func(interactee, interacter)
        new_func.func_name = func.func_name
        return new_func
    return check_interacter


class Trigger(object):
    def __init__(self, game, object_refs=None, actions=None, zones=None, interaction_type=None, conditional=False):
        self.game = game
        self.conditional = conditional
        self.interaction_type = interaction_type

        if object_refs is None:
            self.object_references = {'targets': [], 'conditionals': [], 'interactee': None}
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
        if self.conditional:
            act = action(target_objects)
            cond_act = conditional_action(conditional_objects)(act)
            self.actions.append(cond_act)
        else:
            self.actions.append(action(target_objects)) # last object is Target

    def delete_action(self, action):
        self.actions.remove(action)

    def perf_actions(self, interacter): # called when triggered NOT by a zone
        # TODO take multiple interactees - requires changing the places in code that calls object.functions() for every type of func - AND changing the functions in character_functions_dir
        for a in self.actions:
            interactee = self.game.objects[self.object_references['interactee']]
            a(interactee, interacter)

    def add_zone(self, zone):
        self.zones.append(zone)

    def delete_zone(self, zone):
        self.zones.remove(zone)

    def check_zone_collision(self, interacter):
        pos = interacter.coord
        for z in self.zones:
            if z.collidepoint(pos):
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

    def toggle_conditional(self):
        self.conditional = not self.conditional

        # remake actions with/without the conditional arguments
        acts = [f.__name__ for f in self.actions]
        acts = [trigger_functions_dict[a] for a in acts]
        self.actions = []
        for a in acts:
            self.add_action(a)

    def set_interactee(self, interactee):
        self.object_references['interactee'] = interactee
        self.enable_for_objects()

    def set_interaction_type(self, typ):
        self.interaction_type = typ
        self.enable_for_objects()

    def enable_for_objects(self):
        interactee = self.game.objects[self.object_references['interactee']]

        if not interactee is None and not self.interaction_type is None:
            attr = getattr(interactee, self.interaction_type)
            attr.append(self.perf_actions)

    def create_save_dict(self):
        # TODO fix save/load
        save_dict = {}
        save_dict[u'object_references'] = self.object_references

        act_list = [f.__name__ for f in self.actions]
        save_dict[u'actions'] = json.dumps(act_list)

        save_dict[u'interaction_type'] = self.interaction_type
        save_dict[u'conditional'] = self.conditional

        zones = [json.dumps((z.x, z.y, z.w, z.h)) for z in self.zones]
        save_dict[u'zones'] = zones

        return save_dict

    def __del__(self):
        if not self.object_references['interactee'] is None:
            interactee = self.game.objects[self.object_references['interactee']]
            o_funcs = getattr(interactee, self.interaction_type)
            o_funcs.remove(self.perf_actions)


class TriggerEditor(object):
    def __init__(self, game):
        self.game = game

        self.buttons = {}
        self.drop_lists = {}

        self.trigger_to_edit = None

        self._pos = (0, 0)
        self.pos = (400, self.game.dimensions[1] - 300)

        self.create_elements()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        self._pos = p
        self.update_element_positions()

    def update_element_positions(self):
        size = (120, 20)
        vert_spacing = 5
        horizontal_spacing = 5
        p1 = self.pos[1] - size[1] # pos of TriggerEditor is then top-left of first button
        for b in self.buttons.itervalues():
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

        db = button.DefaultButton

        dl = drop_down_list.DropDownList

        self.buttons['create_new_trigger'] = db(self, self.create_new_trigger, text="New Trigger", order=(0, 0))
        self.drop_lists['triggers'] = dl(self, self.game.map.triggers, self.select_trigger, order=(0, 1))
        self.buttons['delete_trigger'] = db(self, self.delete_selected_trigger, text="Delete Trigger", order=(0, 2))

        self.buttons['interaction_type_label'] = db(self, None, text="Interaction Type", order=(1, 0))
        self.drop_lists['interaction_type'] = dl(self, object_interaction_types, self.set_interaction_type, order=(1, 1))

        self.buttons['pick_interactee'] = db(self, self.pick_interactee, text="Pick Interactee", order=(2, 0))
        self.buttons['pick_interactee_label'] = db(self, None, text="<None>", order=(2, 1))

        # repeat order here as its one or the other
        self.buttons['new_zone'] = db(self, self.create_new_zone, text="New Zone", order=(3, 0))
        self.drop_lists['edit_zones'] = dl(self, {}, self.select_zone, order=(3, 1))

        self.buttons['delete_zone'] = db(self, self.delete_selected_zone, text="Delete Zone", order=(4, 0))
        self.buttons['zone_topleft'] = db(self, self.zone_topleft, text="Select Top Left", order=(4, 1))
        self.buttons['zone_bottomright'] = db(self, self.zone_bottomright, text="Select Bottom Right", order=(4, 2))

        self.buttons['pick_target'] = db(self, self.pick_target, text="Add Target", order=(5, 0))
        self.drop_lists['targets'] = dl(self, {}, self.delete_target, order=(5, 1))

        self.buttons['conditional'] = db(self, self.toggle_conditional, text="Conditional", order=(6, 0))

        self.buttons['pick_conditional'] = db(self, self.pick_conditional, text="New Conditional", order=(7, 0))
        self.drop_lists['conditionals'] = dl(self, {}, self.delete_conditional, order=(7, 1))

        self.buttons['action_label'] = db(self, None, text="Action Add/Delete", order=(8, 0))
        self.drop_lists['new_action'] = dl(self, trigger_functions_dict, self.add_action, order=(8, 1))
        self.drop_lists['actions'] = dl(self, {}, self.delete_action, order=(7, 2))

        self.update_element_positions()

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
        # TODO make setting to defaults (empties) easier?
        trig = self.drop_lists['triggers'].selected
        if trig is None:
            self.drop_lists['edit_zones'].refresh([])
            self.drop_lists['targets'].refresh([])
            self.drop_lists['conditionals'].refresh([])
            self.drop_lists['actions'].refresh([])
            self.buttons['pick_interactee_label'].text = '<None>'
            return

        self.drop_lists['edit_zones'].refresh(trig.zones)
        self.drop_lists['targets'].refresh(trig.object_references['targets'])
        self.drop_lists['conditionals'].refresh(trig.object_references['conditionals'])
        self.drop_lists['actions'].refresh(trig.actions)
        self.buttons['pick_interactee_label'].text = trig.object_references['interactee']

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
            trig.set_interactee(o_name)

            self.buttons['pick_interactee_label'].text = o_name

        self.game.mouse_controller.pick_object(choose)

    def create_new_zone(self):
        trig = self.drop_lists['triggers'].selected

        if trig is None:
            return

        zone = rect.Rect((0, 0), (1, 1))
        trig.add_zone(zone)

        self.drop_lists['edit_zones'].refresh()
        z = zone
        z_name = str(z.x) + ', ' + str(z.y) + ': ' + str(z.w) + ', ' + str(z.h)
        self.drop_lists['edit_zones'].set_to_value(z_name)

    def select_zone(self):
        zone = self.drop_lists['edit_zones'].selected
        if zone is None:
            self.buttons['zone_bottomright'].enabled = False
            self.buttons['zone_bottomright'].visible = False
            self.buttons['zone_topleft'].enabled = False
            self.buttons['zone_topleft'].visible = False
            self.buttons['delete_zone'].enabled = False
            self.buttons['delete_zone'].visible = False
        else:
            self.buttons['zone_bottomright'].enabled = True
            self.buttons['zone_bottomright'].visible = True
            self.buttons['zone_topleft'].enabled = True
            self.buttons['zone_topleft'].visible = True
            self.buttons['delete_zone'].enabled = True
            self.buttons['delete_zone'].visible = True

        self.display_zone(zone)

    def delete_selected_zone(self):
        zone = self.drop_lists['zones'].selected
        trig = self.drop_lists['triggers'].selected
        if zone is None or trig is None:
            return

        trig.delete_zone(zone)

        self.drop_lists['edit_zones'].set_to_default()  # set list to None
        self.drop_lists['edit_zones'].refresh() # update contents of list

    def zone_topleft(self):
        zone = self.drop_lists['edit_zones'].selected
        if zone is None:
            return

        def set_topleft(pos):
            zone.topleft = pos
            self.display_zone(zone)

        self.game.mouse_controller.pick_position(set_topleft)

    def zone_bottomright(self):
        zone = self.drop_lists['edit_zones'].selected
        if zone is None:
            return

        def set_bottomright(pos):
            zone.bottomright = pos
            self.display_zone(zone)

        self.game.mouse_controller.pick_position(set_bottomright)

    def pick_target(self):
        trig = self.drop_lists['triggers'].selected
        if trig is None:
            return

        def choose(target):
            trig.add_target(target)
            self.drop_lists['targets'].refresh() # update contents of list

        self.game.mouse_controller.pick_object(choose)

    def delete_target(self):
        target = self.drop_lists['targets'].selected
        trig = self.drop_lists['triggers'].selected
        if trig is None or target is None:
            return

        trig.delete_target(target)

        self.drop_lists['targets'].set_to_default() # set list to None
        self.drop_lists['targets'].refresh() # update contents of list

    def toggle_conditional(self):
        trig = self.drop_lists['triggers'].selected
        if not trig is None:
            trig.toggle_conditional()

    def pick_conditional(self):
        trig = self.drop_lists['triggers'].selected

        if trig is None:
            return

        def choose(o_name):
            trig.object_references['conditionals'].append(o_name)
            self.drop_lists['conditionals'].refresh()

        self.game.mouse_controller.pick_object(choose)

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


    def display_zone(self, zone):
        pass

    def display_objects(self, objects):
        pass