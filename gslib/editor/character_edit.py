__author__ = 'Martin'

from gslib.ui import button, drop_down_list
from gslib.editor import controls, controls_basic
from gslib.constants import *
from gslib.game_objects import character
from gslib.ui import msg_box
from gslib import window

import io
import os.path

def get_fears_from_file():  # load all possible fears from file, without descriptions
    possible_fears = []
    with io.open(os.path.join(DATA_DIR, "fear_description.txt"), 'rt', encoding='utf-8') as f:
        for l in f:
            fear = l[:l.find(':')]
            if not fear in possible_fears:
                possible_fears.append(fear)
    return possible_fears


class BasicEditor(object):
    def __init__(self, game, toggle_button_text, pos=(0, 0), toggle_pos=(0, 0)):
        self.game = game
        self.pre = ''

        self.toggle_button_text = toggle_button_text
        self.toggle_button_name = self.toggle_button_text.lower()
        self.toggle_button_name = self.toggle_button_name.replace(' ', '_')
        self.toggle_button_name = 'toggle_' + self.toggle_button_name

        self.buttons = {}
        self.drop_lists = {}

        self.enabled = False

        self._pos = (0, 0)
        self.toggle_pos = toggle_pos
        self.buttons[self.toggle_button_name] = button.DefaultButton(self, self.toggle_self, text=toggle_button_text, pos=toggle_pos)

        self.pos = pos

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
            if b.text == self.toggle_button_text:
                continue
            pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
            b.pos = pos
            b.size = size

        for b in self.drop_lists.itervalues():
            pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
            b.pos = pos
            b.size = size


        self.toggle_self(self.enabled)

    def toggle_self(self, value=None):
        if value is None:
            self.enabled = not self.enabled
        else:
            self.enabled = value
        for k, v in self.buttons.iteritems():
            if not k == self.toggle_button_name:
                v.visible = self.enabled
                v.enabled = self.enabled

        for v in self.drop_lists.itervalues():
            v.visible = self.enabled
            v.enabled = self.enabled

        self.buttons[self.toggle_button_name].flip_color_rg(self.enabled)

    def create_elements(self):
        pass


class CharacterTemplateEditor(BasicEditor):
    def __init__(self, game):
        super(CharacterTemplateEditor, self).__init__(game, 'Character Editor', (0, window.height - 160), (0, window.height - 60))
        # self.game = game

        self.pre = 'cte_' # element_name_prefix

        # self.buttons = {}
        # self.drop_lists = {}

        self.char_to_edit = None
        self.char_state_to_edit = None

        # self.enabled = False


        # self._pos = (0, 0)
        self.create_elements()
        # self.pos = (0, window.height - 160)


    # @property
    # def pos(self):
    #     return self._pos
    #
    # @pos.setter
    # def pos(self, p):
    #     self._pos = p
    #     self.update_element_positions()
    #
    # def toggle_self(self, value=None):
    #     if value is None:
    #         self.enabled = not self.enabled
    #     else:
    #         self.enabled = value
    #     for k, v in self.buttons.iteritems():
    #         if not k == 'toggle_character_template_editor':
    #             v.visible = self.enabled
    #             v.enabled = self.enabled
    #
    #     for v in self.drop_lists.itervalues():
    #         v.visible = self.enabled
    #         v.enabled = self.enabled
    #
    #     self.buttons['toggle_character_template_editor'].flip_color_rg(self.enabled)
    #
    #
    # def update_element_positions(self):
    #     size = (120, 20)
    #     vert_spacing = 5
    #     horizontal_spacing = 5
    #     p1 = self.pos[1] - size[1] # pos of TriggerEditor is then top-left of first button
    #     for b in self.buttons.itervalues():
    #         if b.text == "Character Template Editor":
    #             continue
    #         pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
    #         b.pos = pos
    #         b.size = size
    #
    #     for b in self.drop_lists.itervalues():
    #         pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
    #         b.pos = pos
    #         b.size = size
    #
    #
    #     self.toggle_self(self.enabled)


    def create_elements(self): # main buttons that are not character template-dependent
        bu = button.DefaultButton
        dl = drop_down_list.DropDownList

        # self.buttons['toggle_character_template_editor'] = button.DefaultButton(self, self.toggle_self, text="Character Template Editor", pos=(0, window.height - 60))

        self.buttons['new_character'] = bu(self, self.new_character_template, text='New Character Template', order=(-2, 0))

        self.update_element_positions()

    def create_character_elements(self): # re-create for new character
        bu = button.DefaultButton
        dl = drop_down_list.DropDownList

        if self.char_to_edit is None:
            return

        self.buttons['generic_properties_label'] = bu(self, None, text='Generic Properties', order=(-1, 0))
        self.buttons['generic_properties_toggle_label'] = bu(self, None, text='Toggle Edit', order=(-1, 1))

        def bool_flip(p):
            def func():
                new_p = not getattr(self.char_to_edit, p)
                setattr(self.char_to_edit, p, new_p)
                self.buttons[p].flip_color_rg(new_p) # set button colour to reflect true/false
            return func

        def toggle_elements(p):
            if getattr(self.char_to_edit, p): # create controls for them wot need it
                create_controls = {'can_scare': self.create_can_scare_elements,
                                   'can_be_scared': self.create_can_be_scared_elements,
                                   'has_stats': self.create_has_stats_elements,
                                   'can_walk': self.create_can_walk_elements,
                                   'has_special_properties': self.create_has_special_properties_elements,
                                   'has_special_render_properties': self.create_has_special_render_properties_elements,
                                   'has_ai': self.create_has_ai_elements}
                if p in create_controls.keys():
                    create_controls[p]()

        # Toggles
        bool_properties = ['possessor_gets_motion_control', 'possessable', 'can_pick_up', 'can_be_picked_up',
                           'can_scare', 'can_be_scared', 'has_stats', 'can_walk', 'has_special_properties',
                           'has_ai', 'has_special_render_properties']
        for i, p in enumerate(bool_properties):
            str_p = p.replace('_', ' ')
            str_p = str_p.title()
            self.buttons[p] = bu(self, bool_flip(p), text=str_p, order=(i, 0)) # bool toggle of generic character abilities
            self.buttons[p + '_toggle'] = bu(self, toggle_elements(p), text=str_p, order=(i, 1)) # shows/hide editor for specific character ability

            self.buttons[p].flip_color_rg(getattr(self.char_to_edit, p)) # set button colour to reflect true/false

        self.update_element_positions()


    def create_can_scare_elements(self):
        pass # selection of what this char scares

    def create_can_be_scared_elements(self):
        pass # selection of what this char is scared of

    def create_has_stats_elements(self):
        pass # bio, age, etc.

    def create_can_walk_elements(self):
        pass # show walk speed editors

    def create_has_special_properties_elements(self):
        pass # choice of "fire", "wet", etc. Text attributes to base conditional triggers off.

    def create_has_special_render_properties_elements(self):
        pass # trails, etc

    def create_has_ai_elements(self):
        pass # char function editor




    def new_character_template(self):
        self.char_to_edit = character.Character(self.game, 0, 0, 32, 32)
        self.create_character_elements()

    def save_character_template(self):
        pass

    def load_character_template(self):
        pass


    def add_character_state(self):
        def new_state(name):
            if name in self.char_to_edit.states.keys():
                msg_box.InfoBox(self.game, 'State name conflict').show()
            else:
                self.char_to_edit.states[name] = {}
                self.char_state_to_edit = name

        msg_box.InputBox(self.game, 'Enter new state name.', '', new_state).show()

    def select_character_state(self):
        pass

    def delete_character_state(self):
        pass


class ScaresEditor(BasicEditor):
    def __init__(self, game, char, pos, toggle_pos):
        super(ScaresEditor, self).__init__(game, 'Scares Editor', pos=pos, toggle_pos=toggle_pos)
        # self.game = game
        self.pre = 'scares_'
        self.character = char

        self.possible_fears = get_fears_from_file()
        self.possible_fears.append(u'player')