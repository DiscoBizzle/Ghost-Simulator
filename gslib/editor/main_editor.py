from __future__ import absolute_import, division, print_function

import io
import os.path

from gslib import save_load
from gslib.editor import trigger_edit
from gslib.constants import *
from gslib.editor import cutscene, character_edit
from gslib.engine import text
from gslib.game_objects import character_objects, character, game_object, prop_objects
from gslib.ui import button, drop_down_list
from gslib import window
import json


def get_fears_from_file():  # load all possible fears from file, without descriptions
    possible_fears = []
    with io.open(os.path.join(DATA_DIR, "fear_description.txt"), 'rt', encoding='utf-8') as f:
        for l in f:
            fear = l[:l.find(':')]
            if not fear in possible_fears:
                possible_fears.append(fear)
    return possible_fears

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
         'become_unpossessed_functions': 'unpossessed_function',
         'when_scared_functions': 'feared_function',
         'has_touched_functions': 'has_touched_function',
         'is_touched_functions': 'is_touched_function',
         'has_untouched_functions': 'has_untouched_function',
         'is_untouched_functions': 'is_untouched_function',
         'when_harvested_functions': 'harvested_function',
         'idle_functions': 'idle_functions'}
    def func():
        if editor.drop_lists[module].selected:
            a = getattr(editor.object_to_edit, d[module])
            a.append(editor.drop_lists[module].selected(editor.object_to_edit))
    return func


class IntEdit(object):
    def __init__(self, editor, pos, name):
        self.name = name
        self.buttons = {}
        self.buttons[name + '_label'] = button.DefaultButton(self, None, pos=(0, 0), size=(100, 20), text=name)
        self.buttons[name + '_increment'] = button.DefaultButton(self, change_object_value(editor, name, 1), pos=(0, 0),
                                                                 size=(30, 30), text="+")
        self.buttons[name + '_decrement'] = button.DefaultButton(self, change_object_value(editor, name, -1), pos=(0, 0),
                                                                 size=(30, 30), text="-")
        self.buttons[name + '_value'] = button.DefaultButton(self, None, pos=(0, 0), size=(30, 30), text="0")
        self.pos = pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self.buttons[self.name + '_label'].pos = (pos[0], pos[1] + 35)
        self.buttons[self.name + '_increment'].pos = (pos[0] + 70, pos[1])
        self.buttons[self.name + '_decrement'].pos = pos
        self.buttons[self.name + '_value'].pos = (pos[0] + 35, pos[1])
        self._pos = pos


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

        # self.possible_characters = character_objects.possible_characters
        # self.possible_characters = dict(self.possible_characters.items() + prop_objects.possible_props.items())
        self.possible_characters = {}

        self.buttons['place_object_label'] = button.DefaultButton(self, None, pos=(100, window.height - 20), text="Place Object")
        self.drop_lists['place_object'] = drop_down_list.DropDownList(self, self.possible_characters,
                                                                     self.update_object_prototype, pos=(200, window.height - 20), size=(100, 20))
        self.object_prototype = None
        self.get_possible_characters()

        ###################################################################
        # Trigger Editor
        ###################################################################

        self.trigger_editor = trigger_edit.TriggerEditor(self.game)
        self.buttons['toggle_trigger_editor'] = self.trigger_editor.buttons['toggle_trigger_editor']

        self.buttons = dict(self.buttons.items() + self.trigger_editor.buttons.items())
        self.drop_lists = dict(self.drop_lists.items() + self.trigger_editor.drop_lists.items())

        ###################################################################
        # Character Template Editor
        ###################################################################

        self.character_template_editor = character_edit.CharacterTemplateEditor(self.game, self)
        self.buttons['toggle_char_edit'] = self.character_template_editor.toggle_button

        # # add prefix to keys, then combine with main editor buttons
        # char_edit_buttons_prefixed = {}
        # for k, v in self.character_template_editor.buttons.iteritems():
        #     char_edit_buttons_prefixed[self.character_template_editor.pre + k] = v
        #
        #
        # char_edit_lists_prefixed = {}
        # for k, v in self.character_template_editor.drop_lists.iteritems():
        #     char_edit_lists_prefixed[self.character_template_editor.pre + k] = v
        #
        # self.buttons = dict(self.buttons.items() + char_edit_buttons_prefixed.items())
        # self.drop_lists = dict(self.drop_lists.items() + char_edit_lists_prefixed.items())

        ###################################################################
        # Edit object
        ###################################################################
        # self.object_edit_buttons = []
        # self.object_edit_lists = []
        self.object_to_edit = None
        self.object_to_edit_name = None
        # self.show_fears_checklist = False
        # self.show_scared_of_checklist = False

        self.color = (120, 0, 0)
        self.border_color = (120, 50, 80)
        self.high_color = (0, 120, 0)
        self.high_border_color = (0, 200, 0)

        # self.possible_fears = get_fears_from_file()
        # self.possible_fears.append(u'player')

        # self.int_edits = {}

        h_off = 10
        v_off = 400

        # self.create_checklist_buttons()
        # #fears/scared_by checklist show/hide
        # self.buttons['fears_checklist_toggle'] = button.DefaultButton(self, self.toggle_fears_checklist,
        #                                                               pos=(window.width - 100 - h_off, window.height - v_off - 70),
        #                                                               size=(100, 20), text="Fears")
        # self.buttons['scared_of_checklist_toggle'] = button.DefaultButton(self, self.toggle_scared_of_checklist,
        #                                                               pos=(window.width - 210 - h_off, window.height - v_off - 70),
        #                                                               size=(100, 20), text="Scared Of")
        #
        # # speed and weight edit button sets.
        # self.int_edits['normal_speed'] = IntEdit(self, (window.width - 210 - h_off, window.height - v_off - 35), 'normal_speed')
        # self.int_edits['feared_speed'] = IntEdit(self, (window.width - 100 - h_off, window.height - v_off - 35), 'feared_speed')
        # self.int_edits['collision_weight'] = IntEdit(self, (window.width - 320 - h_off, window.height - v_off - 35), 'collision_weight')
        #
        # for ie in self.int_edits.itervalues():
        #     self.buttons = dict(self.buttons.items() + ie.buttons.items())

        # name edit
        # age edit

        # v_ind = 0
        # # function edit
        # self.show_function_edit = False
        # self.function_edit_buttons = []
        # self.function_edit_lists = []
        # self.buttons['function_edit_toggle'] = button.DefaultButton(self, self.toggle_function_edit,
        #                                                               pos=(window.width - 320 - h_off, window.height - v_off - 70),
        #                                                               size=(100, 20), text="Function Edit", visible=False, enabled=False)
        # self.object_edit_buttons.append('function_edit_toggle')
        # for module, func_dict in character_functions.all_functions_dict.iteritems():
        #     #display button
        #     self.buttons[module] = button.DefaultButton(self, None,
        #                                                 pos=(100, window.height - 200 - v_ind * 40),
        #                                                 size=(200, 20), text=module, visible=False, enabled=False)
        #     self.function_edit_buttons.append(module)
        #     # drop list to choose funciton for each object event type
        #     self.drop_lists[module] = drop_down_list.DropDownList(self, func_dict,
        #                                                           set_function(self, module), pos=(300, window.height - 200 - v_ind * 40),
        #                                                           size=(200, 20), visible=False, enabled=False)
        #     self.function_edit_lists.append(module)
        #     v_ind += 1

        self.buttons['delete_selection'] = button.DefaultButton(self, self.delete_selected_object,
                                                        pos=(window.width - 210 - h_off, window.height - v_off - 200),
                                                        size=(100, 20), text="Delete Object", visible=True)
        #
        #
        # self.object_edit_buttons += ['fears_checklist_toggle', 'scared_of_checklist_toggle',
        #                             'normal_speed_label', 'normal_speed_increment', 'normal_speed_decrement', 'normal_speed_value',
        #                             'feared_speed_label', 'feared_speed_increment', 'feared_speed_decrement', 'feared_speed_value',
        #                             'collision_weight_label', 'collision_weight_increment', 'collision_weight_decrement', 'collision_weight_value',
        #                             'delete_selection']
        # for v in self.object_edit_buttons:
        #     self.buttons[v].visible = False
        #     self.buttons[v].enabled = False
        # for v in self.object_edit_lists:
        #     self.drop_lists[v].visible = False
        #     self.drop_lists[v].enabled = False

        ###################################################################
        # Cutscene editor
        ###################################################################
        self.cutscene_editor = cutscene.CutsceneEditor(self.game, self)

        ###################################################################
        # Other buttons
        ###################################################################
        self.buttons['save_map'] = button.DefaultButton(self, self.save_map,
                                                        pos=(window.width - 100 - h_off, window.height - v_off - 200),
                                                        size=(100, 20), text="Save Map", visible=True)

        self.buttons['undo'] = button.DefaultButton(self, self.undo,
                                                        pos=(window.width - 210 - h_off, window.height - v_off - 170),
                                                        size=(100, 20), text="Undo", visible=True)

        self.buttons['redo'] = button.DefaultButton(self, self.redo,
                                                        pos=(window.width - 100 - h_off, window.height - v_off - 170),
                                                        size=(100, 20), text="Redo", visible=True)

        self.stored_button_enabled_state = {'place_object_label': True, 'toggle_trigger_editor': True,
                                            'delete_selection': True, 'toggle_char_edit': True, 'save_map': True,
                                            'undo': True, 'redo': True}
        self.stored_list_enabled_state = {'place_object': True}

    def list_to_dict_shabby(self, base_key, l):
        k = 0
        d = {}

        for el in l:
            d[base_key + str(k)] = el
            k += 1

        return d

    def get_possible_characters(self):
        self.possible_characters.clear()

        def create_char(dictionary):
            def func(game):
                ch = character.Character(game, 0, 0, 32, 32)
                ch.load_from_dict(dictionary)
                return ch
            return func


        for fil_name in os.listdir(CHARACTERS_DIR):
            if fil_name.endswith(".char"):
                with io.open(os.path.join(CHARACTERS_DIR, fil_name), 'r', encoding='utf-8') as f:
                    dic = json.load(f)
                    self.possible_characters[fil_name[:-5]] = create_char(dic)

        self.drop_lists['place_object'].refresh()

    def get_buttons(self):
        cutscene_dict = dict(self.buttons, **self.list_to_dict_shabby('editor_cutscene_b_', self.cutscene_editor.buttons))
        char_edit_dict = dict(cutscene_dict, **self.character_template_editor.get_buttons())
        return char_edit_dict

    def get_lists(self):

        cutscene_dict = dict(self.drop_lists, **self.list_to_dict_shabby('editor_cutscene_l_', self.cutscene_editor.lists))
        char_edit_dict = dict(cutscene_dict, **self.character_template_editor.get_lists())
        return char_edit_dict

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
        self.character_template_editor.toggle_self(False)

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
            self.drop_lists['triggers'].refresh()
        self.enable_main_editor()

    def exit_edit_mode(self):
        self.save_state = save_load.create_save_state(self.game.map)
        self.disable_main_editor()

    def delete_selected_object(self):
        del self.game.map.objects[self.object_to_edit_name]
        self.game.gather_objects()

    def save_map(self):
        save_load.save_map(self.game.map)

    def toggle_button_color(self, b, setting=None):
        if setting is None:  # flip color
            if b.color == self.color:
                b.color = self.high_color
                b.border_color = self.high_border_color
            else:
                b.color = self.color
                b.border_color = self.border_color
        else:  # set to high color if setting is not False or 0
            if setting and b.color != self.high_color:  # only update color if needed, more efficient
                b.color = self.high_color
                b.border_color = self.high_border_color
            elif not setting and b.color != self.color:
                b.color = self.color
                b.border_color = self.border_color

    def handle_object_click(self, o_name):
        self.object_to_edit_selected(o_name)

    def handle_map_click(self, pos):
        pass

    def object_to_edit_selected(self, o_name):  # show object editing options when an object is selected
        self.object_to_edit_name = o_name
        if self.object_to_edit_name:
            self.object_to_edit = self.game.objects[o_name]
        else:
            self.object_to_edit = None

    def update_object_prototype(self):
        if self.drop_lists['place_object'].selected:
            self.object_prototype = self.drop_lists['place_object'].selected(self.game)
            self.object_prototype.current_speed = 0
        else:
            self.object_prototype = None
        self.game.cursor = self.object_prototype
        self.game.gather_objects()

    def update(self):
        self.cutscene_editor.update()

    def draw(self):
        buttons = self.get_buttons()
        lists = self.get_lists()
        for b in buttons.itervalues():
            b.draw()
        for dl in lists.itervalues():
            dl.main_button.draw()
        for dl in lists.itervalues():
            if dl.open:
                for b in dl.drop_buttons:
                    b.draw()
                if hasattr(dl, 'slider'):
                    dl.slider.draw()
