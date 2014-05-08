from gslib import drop_down_list
from gslib import button
from gslib import character_objects
from gslib import game_object
from gslib import graphics
from gslib import triggers
from gslib import text
from gslib import character_functions
from gslib import save_load
from gslib.constants import *
from gslib.editor import cutscene


def set_fear_button(editor, fear):
    def func():
        editor.set_fear(fear)
    return func


def change_object_value(editor, which, increment):
    func = None
    if which == 'feared_speed':
        def func():
            editor.object_to_edit.feared_speed += increment
            if editor.object_to_edit.feared_speed < 0:
                editor.object_to_edit.feared_speed = 0
            editor.buttons['feared_speed_value'].text = str(editor.object_to_edit.feared_speed)

    elif which == 'normal_speed':
        def func():
            editor.object_to_edit.normal_speed += increment
            if editor.object_to_edit.normal_speed < 0:
                editor.object_to_edit.normal_speed = 0
            editor.buttons['normal_speed_value'].text = str(editor.object_to_edit.normal_speed)

    elif which == 'collision_weight':
        def func():
            editor.object_to_edit.collision_weight += increment
            if editor.object_to_edit.collision_weight < 0:
                editor.object_to_edit.collision_weight = 0
            editor.buttons['collision_weight_value'].text = str(editor.object_to_edit.collision_weight)

    return func


def set_function(editor, module):
    d = {'become_possessed_functions': 'possessed_function',
         'when_scared_functions': 'feared_function',
         'has_touched_functions': 'has_touched_function',
         'become_unpossessed_functions': 'unpossessed_function',
         'when_harvested_functions': 'harvested_function'}
    def func():
        if editor.drop_lists[module].selected:
            a = getattr(editor.object_to_edit, d[module])
            a.append(editor.drop_lists[module].selected(editor.object_to_edit))
    return func


class IntEdit(object):
    def __init__(self, editor, pos, name):
        self._pos = pos
        self.name = name
        self.buttons = {}
        self.buttons[name + '_label'] = button.DefaultButton(self, None, pos=(0, 0), size=(100, 20), text=name)
        self.buttons[name + '_increment'] = button.DefaultButton(self, change_object_value(editor, name, 1), pos=(0, 0),
                                                                 size=(30, 30), text="+")
        self.buttons[name + '_decrement'] = button.DefaultButton(self, change_object_value(editor, name, -1), pos=(0, 0),
                                                                 size=(30, 30), text="-")
        self.buttons[name + '_value'] = button.DefaultButton(self, None, pos=(0, 0), size=(30, 30), text="0")
        self.set_pos(pos)

    def get_pos(self):
        return self._pos

    def set_pos(self, pos):
        self.buttons[self.name + '_label'].pos = (pos[0], pos[1] + 35)
        self.buttons[self.name + '_increment'].pos = (pos[0] + 70, pos[1])
        self.buttons[self.name + '_decrement'].pos = pos
        self.buttons[self.name + '_value'].pos = (pos[0] + 35, pos[1])
        self._pos = pos

    pos = property(get_pos, set_pos)


class Cursor(game_object.GameObject):
    def __init__(self, game, sprite):
        game_object.GameObject.__init__(self, game, 0, 0, 0, 0, None)
        self.max_frames = 0
        self.current_speed = 0
        self.normal_speed = 0

        self.update = lambda: None

        self.sprite = sprite
        self.is_cursor = True


class Editor(object):
    def __init__(self, game):
        self.game = game

        self.save_state = None # to go back to when you re-open editor after testing your changes
        self.undo_states = []
        self.undo_index = 0

        self.text_sprites = {}
        self.font_size = 20

        self.buttons = {}
        self.drop_lists = {}

        ###################################################################
        # Place new object
        ###################################################################

        self.possible_characters = {'Small Door': character_objects.SmallDoor,
                                    'Dude': character_objects.Dude}

        self.buttons['pick_object_label'] = button.DefaultButton(self, None, pos=(100, self.game.dimensions[1] - 20), text="Place Object")
        self.drop_lists['pick_object'] = drop_down_list.DropDownList(self, self.possible_characters,
                                                                     self.update_object_prototype, pos=(200, self.game.dimensions[1] - 20))
        self.object_prototype = None

        ###################################################################
        # View/Edit existing Trigger
        ###################################################################

        self.buttons['view_triggers_label'] = button.DefaultButton(self, None, pos=(320, self.game.dimensions[1] - 20), size=(120, 20),
                                                                   text="Current Triggers")
        self.drop_lists['view_triggers'] = drop_down_list.DropDownList(self, self.game.map.triggers,
                                                                       self.display_trigger, pos=(440, self.game.dimensions[1] - 20),
                                                                       labels='classname', size=(300, 20))
        self.buttons['delete_trigger'] = button.DefaultButton(self, self.delete_selected_trigger, pos=(320, self.game.dimensions[1] - 40), size=(120, 20),
                                                                   text="Delete Trigger")
        self.trigger_display_colours = ((120, 0, 0), (0, 120, 0), (0, 0, 120), (120, 120, 0), (120, 0, 120), (0, 120, 120), (120, 120, 120))
        self.trigger_display_circles = []
        self.trigger_display_text = []
        self.trigger_to_edit = None


        self.drop_lists['add_actions'] = drop_down_list.DropDownList(self, triggers.trigger_functions_dict,
                                                                     self.add_action_to_trigger, pos=(440, self.game.dimensions[1] - 50),
                                                                     size=(300, 20))

        ###################################################################
        # Create new Trigger
        ###################################################################

        self.possible_triggers = triggers.possible_triggers
        # self.possible_triggers = {'Flip State On Harvest': triggers.FlipStateOnHarvest,
        #                           'Flip State When Touched (Conditional)': triggers.FlipStateWhenTouchedConditional,
        #                           'Flip State When UnTouched (Conditional)': triggers.FlipStateWhenUnTouchedConditional}
        self.buttons['new_trigger_label'] = button.DefaultButton(self, None, pos=(760, self.game.dimensions[1] - 20), size=(100, 20),
                                                                 text="New trigger")
        self.drop_lists['new_triggers'] = drop_down_list.DropDownList(self, self.possible_triggers,
                                                                      self.new_trigger, pos=(860, self.game.dimensions[1] - 20),
                                                                      size=(300, 20))
        # self.new_trigger_objects = []
        self.trigger_prototype = None

        ###################################################################
        # Edit object
        ###################################################################
        self.object_edit_buttons = []
        self.object_edit_lists = []
        self.object_to_edit = None
        self.object_to_edit_name = None
        self.show_fears_checklist = False
        self.show_scared_of_checklist = False

        self.colour = (120, 0, 0)
        self.border_colour = (120, 50, 80)
        self.high_colour = (0, 120, 0)
        self.high_border_colour = (0, 200, 0)

        self.possible_fears = [u'player']
        self.get_fears_from_file()

        self.int_edits = {}

        h_off = 10
        v_off = 400

        self.create_checklist_buttons()
        #fears/scared_by checklist show/hide
        self.buttons['fears_checklist_toggle'] = button.DefaultButton(self, self.toggle_fears_checklist,
                                                                      pos=(self.game.dimensions[0] - 100 - h_off, self.game.dimensions[1] - v_off - 70),
                                                                      size=(100, 20), text="Fears")
        self.buttons['scared_of_checklist_toggle'] = button.DefaultButton(self, self.toggle_scared_of_checklist,
                                                                      pos=(self.game.dimensions[0] - 210 - h_off, self.game.dimensions[1] - v_off - 70),
                                                                      size=(100, 20), text="Scared Of")

        # speed and weight edit button sets.
        self.int_edits['normal_speed'] = IntEdit(self, (self.game.dimensions[0] - 210 - h_off, self.game.dimensions[1] - v_off - 35), 'normal_speed')
        self.int_edits['feared_speed'] = IntEdit(self, (self.game.dimensions[0] - 100 - h_off, self.game.dimensions[1] - v_off - 35), 'feared_speed')
        self.int_edits['collision_weight'] = IntEdit(self, (self.game.dimensions[0] - 320 - h_off, self.game.dimensions[1] - v_off - 35), 'collision_weight')

        for ie in self.int_edits.itervalues():
            self.buttons = dict(self.buttons.items() + ie.buttons.items())

        # name edit
        # age edit

        v_ind = 0
        # function edit
        self.show_function_edit = False
        self.function_edit_buttons = []
        self.function_edit_lists = []
        self.buttons['function_edit_toggle'] = button.DefaultButton(self, self.toggle_function_edit,
                                                                      pos=(self.game.dimensions[0] - 320 - h_off, self.game.dimensions[1] - v_off - 70),
                                                                      size=(100, 20), text="Function Edit", visible=False, enabled=False)
        self.object_edit_buttons.append('function_edit_toggle')
        for module, func_dict in character_functions.all_functions_dict.iteritems():
            #display button
            self.buttons[module] = button.DefaultButton(self, None,
                                                        pos=(100, self.game.dimensions[1] - 200 - v_ind * 40),
                                                        size=(200, 20), text=module, visible=False, enabled=False)
            self.function_edit_buttons.append(module)
            # drop list to choose funciton for each object event type
            self.drop_lists[module] = drop_down_list.DropDownList(self, func_dict,
                                                                  set_function(self, module), pos=(300, self.game.dimensions[1] - 200 - v_ind * 40),
                                                                  size=(200, 20), visible=False, enabled=False)
            self.function_edit_lists.append(module)
            v_ind += 1

        self.buttons['delete_selection'] = button.DefaultButton(self, self.delete_selected_object,
                                                        pos=(self.game.dimensions[0] - 210 - h_off, self.game.dimensions[1] - v_off - 200),
                                                        size=(100, 20), text="Delete Object", visible=True, enabled=True)


        self.object_edit_buttons += ['fears_checklist_toggle', 'scared_of_checklist_toggle',
                                    'normal_speed_label', 'normal_speed_increment', 'normal_speed_decrement', 'normal_speed_value',
                                    'feared_speed_label', 'feared_speed_increment', 'feared_speed_decrement', 'feared_speed_value',
                                    'collision_weight_label', 'collision_weight_increment', 'collision_weight_decrement', 'collision_weight_value',
                                    'delete_selection']
        for v in self.object_edit_buttons:
            self.buttons[v].visible = False
            self.buttons[v].enabled = False
        for v in self.object_edit_lists:
            self.drop_lists[v].visible = False
            self.drop_lists[v].enabled = False

        ###################################################################
        # Cutscene editor
        ###################################################################
        self.cutscene_editor = cutscene.CutsceneEditor(self.game, self)

        ###################################################################
        # Other buttons
        ###################################################################
        self.buttons['save_map'] = button.DefaultButton(self, self.save_map,
                                                        pos=(self.game.dimensions[0] - 100 - h_off, self.game.dimensions[1] - v_off - 200),
                                                        size=(100, 20), text="Save Map", visible=True, enabled=True)

        self.buttons['undo'] = button.DefaultButton(self, self.undo,
                                                        pos=(self.game.dimensions[0] - 210 - h_off, self.game.dimensions[1] - v_off - 170),
                                                        size=(100, 20), text="Undo", visible=True, enabled=True)

        self.buttons['redo'] = button.DefaultButton(self, self.redo,
                                                        pos=(self.game.dimensions[0] - 100 - h_off, self.game.dimensions[1] - v_off - 170),
                                                        size=(100, 20), text="Redo", visible=True, enabled=True)

        self.stored_button_enabled_state = {}
        self.stored_list_enabled_state = {}

    def list_to_dict_shabby(self, base_key, l):
        k = 0
        d = {}

        for el in l:
            d[base_key + str(k)] = el
            k += 1

        return d

    def get_buttons(self):
        return dict(self.buttons, **self.list_to_dict_shabby('editor_cutscene_b_', self.cutscene_editor.buttons))

    def get_lists(self):
        return dict(self.drop_lists, **self.list_to_dict_shabby('editor_cutscene_l_', self.cutscene_editor.lists))

    def create_undo_state(self):
        n_history = 200
        state = save_load.create_save_state(self.game.map)

        if self.undo_index < len(self.undo_states) - 1: # delete redo info if have undone stuff and then do new things
            self.undo_states = self.undo_states[:self.undo_index]

        self.undo_states.append(state)
        self.undo_index += 1
        if len(self.undo_states) > n_history:
            self.undo_index = n_history - 1


    def undo(self):
        if self.undo_index > 0:
            self.undo_index -= 1
            save_load.restore_save_state(self.game, self.game.map, self.undo_states[self.undo_index])

    def redo(self):
        if self.undo_index < len(self.undo_states) - 1:
            self.undo_index += 1
            save_load.restore_save_state(self.game, self.game.map, self.undo_states[self.undo_index])

    def disable_main_editor(self):
        for bk, bv in self.buttons.iteritems():
            self.stored_button_enabled_state[bk] = bv.enabled
            bv.enabled = False
        for lk, lv in self.drop_lists.iteritems():
            self.stored_list_enabled_state[lk] = lv.enabled
            lv.enabled = False

    def enable_main_editor(self):
        for bk, be in self.stored_button_enabled_state.iteritems():
            self.buttons[bk].enabled = be
        for lk, le in self.stored_list_enabled_state.iteritems():
            self.drop_lists[lk].enabled = le
        self.stored_button_enabled_state = {}
        self.stored_list_enabled_state = {}

    def enter_edit_mode(self):
        if not self.save_state is None:
            save_load.restore_save_state(self.game, self.game.map, self.save_state)
            # refresh all things that refer to specific entities that have been re-created
            self.drop_lists['view_triggers'].refresh()

    def exit_edit_mode(self):
        self.save_state = save_load.create_save_state(self.game.map)

    def delete_selected_object(self):
        del self.game.map.objects[self.object_to_edit_name]
        self.game.gather_buttons_and_drop_lists_and_objects()

    def delete_selected_trigger(self):
        if not self.drop_lists['view_triggers'].selected is None:
            del self.game.map.triggers[self.drop_lists['view_triggers'].selected_name]
            self.drop_lists['view_triggers'].selected.__del__() # TODO work out why del <thing> doesn't work here
            # del self.drop_lists['view_triggers'].selected

            drop_down_list.list_func(self.drop_lists['view_triggers'], None)()
            self.drop_lists['view_triggers'].refresh()

    def save_map(self):
        save_load.save_map(self.game.map)

    def toggle_function_edit(self, state=None):
        if state is None:
            self.show_function_edit = not self.show_function_edit
        else:
            self.show_function_edit = state
        self.toggle_button_colour(self.buttons['function_edit_toggle'], self.show_function_edit)
        for n in self.function_edit_buttons:
            self.buttons[n].visible = self.show_function_edit
            self.buttons[n].enabled = self.show_function_edit
        for n in self.function_edit_lists:
            self.drop_lists[n].visible = self.show_function_edit
            self.drop_lists[n].enabled = self.show_function_edit

    def toggle_fears_checklist(self):  # flip between checklists, or just show/hide one
        self.show_fears_checklist = not self.show_fears_checklist
        self.show_scared_of_checklist = False
        self.toggle_button_colour(self.buttons['scared_of_checklist_toggle'], self.show_scared_of_checklist)
        self.toggle_button_colour(self.buttons['fears_checklist_toggle'], self.show_fears_checklist)
        self.display_fears_checklist()

    def toggle_scared_of_checklist(self):  # flip between checklists, or just show/hide one
        self.show_scared_of_checklist = not self.show_scared_of_checklist
        self.show_fears_checklist = False
        self.toggle_button_colour(self.buttons['scared_of_checklist_toggle'], self.show_scared_of_checklist)
        self.toggle_button_colour(self.buttons['fears_checklist_toggle'], self.show_fears_checklist)
        self.display_fears_checklist()

    def display_fears_checklist(self):
        for f in self.possible_fears:
            if self.show_scared_of_checklist or self.show_fears_checklist:  # only show the checklist if either checklist is active
                self.buttons[f].visible = True
                self.buttons[f].enabled = True
            else:
                self.buttons[f].visible = False
                self.buttons[f].enabled = False
            if self.show_fears_checklist:  # highlight those that are in o.fears
                if f in self.object_to_edit.fears:
                    self.toggle_button_colour(self.buttons[f], 1)
                else:
                    self.toggle_button_colour(self.buttons[f], 0)
            elif self.show_scared_of_checklist:  # highlight those that are in o.scared_of
                if f in self.object_to_edit.scared_of:
                    self.toggle_button_colour(self.buttons[f], 1)
                else:
                    self.toggle_button_colour(self.buttons[f], 0)

    def toggle_button_colour(self, b, setting=None):
        if setting is None:  # flip colour
            if b.colour == self.colour:
                b.colour = self.high_colour
                b.border_colour = self.high_border_colour
            else:
                b.colour = self.colour
                b.border_colour = self.border_colour
        else:  # set to high colour if setting is not False or 0
            if setting and b.colour != self.high_colour:  # only update colour if needed, more efficient
                b.colour = self.high_colour
                b.border_colour = self.high_border_colour
            elif not setting and b.colour != self.colour:
                b.colour = self.colour
                b.border_colour = self.border_colour

    def handle_object_click(self, o_name):
        self.object_to_edit_selected(o_name)

    def handle_map_click(self, pos):
        pass

    def object_to_edit_selected(self, o_name):  # show object editing options when an object is selected
        self.object_to_edit_name = o_name
        if self.object_to_edit_name:
            self.object_to_edit = self.game.objects[o_name]
            self.buttons['feared_speed_value'].text = str(self.object_to_edit.feared_speed)
            self.buttons['normal_speed_value'].text = str(self.object_to_edit.normal_speed)
            self.buttons['collision_weight_value'].text = str(self.object_to_edit.collision_weight)
            for v in self.object_edit_buttons:
                self.buttons[v].visible = True
                self.buttons[v].enabled = True
            for v in self.object_edit_lists:
                self.drop_lists[v].visible = True
                self.drop_lists[v].enabled = True
        else:
            self.show_fears_checklist = False
            self.show_scared_of_checklist = False
            self.toggle_button_colour(self.buttons['scared_of_checklist_toggle'], 0)
            self.toggle_button_colour(self.buttons['fears_checklist_toggle'], 0)
            for v in self.object_edit_buttons:
                self.buttons[v].visible = False
                self.buttons[v].enabled = False
            for v in self.object_edit_lists:
                self.drop_lists[v].visible = False
                self.drop_lists[v].enabled = False
            self.toggle_function_edit(False)
        self.display_fears_checklist()  # update on change selection

    def create_checklist_buttons(self):  # puts a button for each fear into the buttons dict
        ndown = 6
        for i, f in enumerate(self.possible_fears):
            pos = ((i / ndown) * 105, self.game.dimensions[1] - 200 - (i % ndown) * 25)
            self.buttons[f] = button.DefaultButton(self, set_fear_button(self, f), pos=pos,
                                                   size=(100, 20), text=f, visible=False, enabled=False)

    def set_fear(self, fear):  # adds/removes either fears or scared_ofs on button click
        self.toggle_button_colour(self.buttons[fear])
        if self.show_fears_checklist:
            if fear in self.object_to_edit.fears:
                self.object_to_edit.fears.remove(fear)
            else:
                self.object_to_edit.fears.append(fear)

        elif self.show_scared_of_checklist:
            if fear in self.object_to_edit.scared_of:
                self.object_to_edit.scared_of.remove(fear)
            else:
                self.object_to_edit.scared_of.append(fear)

    def get_fears_from_file(self):  # load all possible fears from file, without descriptions
        f = open(os.path.join(CHARACTER_DIR, "fear_description.txt"), 'r')
        for l in f:
            fear = l[:l.find(':')].decode('utf-8')
            if not fear in self.possible_fears:
                self.possible_fears.append(fear)

    def update_object_prototype(self):
        if self.drop_lists['pick_object'].selected:
            self.object_prototype = self.drop_lists['pick_object'].selected(self.game)
            self.object_prototype.current_speed = 0
            self.object_prototype.normal_speed = 0
            #set everything to None when i can be bothered
        else:
            self.object_prototype = None
        self.game.cursor = self.object_prototype
        self.game.gather_buttons_and_drop_lists_and_objects()

    def draw_trigger(self, t):
        self.trigger_display_circles = []
        self.trigger_display_text = []
        # t = self.drop_lists['view_triggers'].selected
        if t:
            # font = pygame.font.SysFont(FONT, 20)
            for i, o_name in enumerate(t.object_references):
                if o_name is None:
                    continue
                circ = graphics.draw_circle(25, self.trigger_display_colours[i])
                # circ.set_position(o.coord[0], o.coord[1])
                te = self.create_text_sprite(t.legend[i])  # font.render(t.legend[i], True, (255, 255, 255))
                # t.set_position(o.coord[0, o.coord[1]])
                self.trigger_display_circles.append((circ, self.game.objects[o_name]))
                self.trigger_display_text.append((te, self.game.objects[o_name]))

    def create_text_sprite(self, tex):
        if not tex in self.text_sprites.keys():
            self.text_sprites[tex] = text.new(text=tex, font_size=self.font_size, centered=True)
            self.text_sprites[tex].color = (200, 200, 200, 255)
        return self.text_sprites[tex]

    def display_trigger(self):
        self.draw_trigger(self.drop_lists['view_triggers'].selected)
        self.trigger_to_edit = self.drop_lists['view_triggers'].selected

    def add_action_to_trigger(self):
        trig = self.trigger_to_edit
        trig.add_action(self.drop_lists['add_actions'].selected)

    def create_trigger_cursor(self, tex):
        t = self.create_text_sprite(tex)
        self.game.cursor = Cursor(self.game, t)
        self.game.gather_buttons_and_drop_lists_and_objects()

    def new_trigger(self):
        if self.drop_lists['new_triggers'].selected:
            self.trigger_prototype = self.drop_lists['new_triggers'].selected(self.game)
            # self.game.new_trigger_capture = True
            self.create_trigger_cursor(self.trigger_prototype.legend[0])
            self.game.mouse_controller.pick_object(self.update_new_trigger)

    def update_new_trigger(self, o_name):
        t = self.trigger_prototype
        l = t.object_references
        l.append(o_name)

        target_number = len(self.trigger_prototype.legend)
        if len(l) == target_number:
            name = self.trigger_prototype.__class__.__name__
            while True:
                if name in self.game.map.triggers.keys():
                    name += '0'
                else:
                    break
            self.game.map.triggers[name] = self.drop_lists['new_triggers'].selected(self.game, *l)
            self.draw_trigger(None)
            self.game.cursor = None
            self.game.gather_buttons_and_drop_lists_and_objects()

            self.drop_lists['new_triggers'].selected = None
            self.drop_lists['new_triggers'].drop_buttons[0].perf_function()  # call the <None> function
            # self.game.new_trigger_capture = False
            self.trigger_prototype = None

            self.drop_lists['view_triggers'].refresh()

            self.create_undo_state()
        else:
            self.game.mouse_controller.pick_object(self.update_new_trigger)
            self.create_trigger_cursor(self.trigger_prototype.legend[len(l)])

            self.draw_trigger(t)

    def update(self):
        self.cutscene_editor.update()


