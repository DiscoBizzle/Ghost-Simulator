import pygame
from gslib import drop_down_list
from gslib import button
from gslib import character_objects
from gslib import game_object
from gslib import graphics
from gslib import triggers
from gslib import text
from gslib.constants import *


def none():
    pass


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


class Cursor(game_object.GameObject):
    def __init__(self, game, sprite):
        game_object.GameObject.__init__(self, game, 0, 0, 0, 0, None)
        self.max_frames = 0
        self.current_speed = 0
        self.normal_speed = 0

        self.update = none

        self.sprite = sprite
        self.is_cursor = True


class Editor(object):
    def __init__(self, game):
        self.game = game
        # self.pos = pos

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
        # View existing Trigger
        ###################################################################

        self.buttons['view_triggers_label'] = button.DefaultButton(self, None, pos=(320, self.game.dimensions[1] - 20), size=(120, 20),
                                                                   text="Current Triggers")
        self.drop_lists['view_triggers'] = drop_down_list.DropDownList(self, self.game.map.triggers,
                                                                       self.display_trigger, pos=(440, self.game.dimensions[1] - 20),
                                                                       labels='classname', size=(300, 20))
        self.trigger_display_colours = ((120, 0, 0), (0, 120, 0), (0, 0, 120), (120, 120, 0), (120, 0, 120), (0, 120, 120), (120, 120, 120))
        self.trigger_display_circles = []
        self.trigger_display_text = []

        ###################################################################
        # Create new Trigger
        ###################################################################

        self.possible_triggers = {'Flip State On Harvest': triggers.FlipStateOnHarvest,
                                  'Flip State When Touched (Conditional)': triggers.FlipStateWhenTouchedConditional,
                                  'Flip State When UnTouched (Conditional)': triggers.FlipStateWhenUnTouchedConditional}
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
        self.object_to_edit = None
        self.show_fears_checklist = False
        self.show_scared_of_checklist = False

        self.colour = (120, 0, 0)
        self.border_colour = (120, 50, 80)
        self.high_colour = (0, 120, 0)
        self.high_border_colour = (0, 200, 0)

        self.possible_fears = [u'player']
        self.get_fears_from_file()

        h_off = 10
        v_off = 250

        self.create_checklist_buttons()
        #fears/scared_by checklist show/hide
        self.buttons['fears_checklist_toggle'] = button.DefaultButton(self, self.toggle_fears_checklist,
                                                                      pos=(self.game.dimensions[0] - 100 - h_off, self.game.dimensions[1] - v_off - 70),
                                                                      size=(100, 20), text="Fears")
        self.buttons['scared_of_checklist_toggle'] = button.DefaultButton(self, self.toggle_scared_of_checklist,
                                                                      pos=(self.game.dimensions[0] - 210 - h_off, self.game.dimensions[1] - v_off - 70),
                                                                      size=(100, 20), text="Scared Of")
        # normal speed
        self.buttons['normal_speed_label'] = button.DefaultButton(self, None,
                                                                      pos=(self.game.dimensions[0] - 210 - h_off, self.game.dimensions[1] - v_off),
                                                                      size=(100, 20), text="Normal Speed")
        self.buttons['normal_speed_increment'] = button.DefaultButton(self, change_object_value(self, 'normal_speed', 1),
                                                                      pos=(self.game.dimensions[0] - 140 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="+")
        self.buttons['normal_speed_decrement'] = button.DefaultButton(self, change_object_value(self, 'normal_speed', -1),
                                                                      pos=(self.game.dimensions[0] - 210 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="-")
        self.buttons['normal_speed_value'] = button.DefaultButton(self, None,
                                                                      pos=(self.game.dimensions[0] - 175 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="0")

        # feared speed
        self.buttons['feared_speed_label'] = button.DefaultButton(self, None,
                                                                      pos=(self.game.dimensions[0] - 100 - h_off, self.game.dimensions[1] - v_off),
                                                                      size=(100, 20), text="Feared Speed")
        self.buttons['feared_speed_increment'] = button.DefaultButton(self, change_object_value(self, 'feared_speed', 1),
                                                                      pos=(self.game.dimensions[0] - 30 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="+")
        self.buttons['feared_speed_decrement'] = button.DefaultButton(self, change_object_value(self, 'feared_speed', -1),
                                                                      pos=(self.game.dimensions[0] - 100 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="-")
        self.buttons['feared_speed_value'] = button.DefaultButton(self, None,
                                                                      pos=(self.game.dimensions[0] - 65 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="0")

        # collision weight
        self.buttons['collision_weight_label'] = button.DefaultButton(self, None,
                                                                      pos=(self.game.dimensions[0] - 320 - h_off, self.game.dimensions[1] - v_off),
                                                                      size=(100, 20), text="Collision Weight")
        self.buttons['collision_weight_increment'] = button.DefaultButton(self, change_object_value(self, 'collision_weight', 1),
                                                                      pos=(self.game.dimensions[0] - 250 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="+")
        self.buttons['collision_weight_decrement'] = button.DefaultButton(self, change_object_value(self, 'collision_weight', -1),
                                                                      pos=(self.game.dimensions[0] - 320 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="-")
        self.buttons['collision_weight_value'] = button.DefaultButton(self, None,
                                                                      pos=(self.game.dimensions[0] - 285 - h_off, self.game.dimensions[1] - v_off - 35),
                                                                      size=(30, 30), text="0")

        # name edit
        # age edit

        # function edit


        self.object_edit_buttons = ['fears_checklist_toggle', 'scared_of_checklist_toggle',
                                    'normal_speed_label', 'normal_speed_increment', 'normal_speed_decrement', 'normal_speed_value',
                                    'feared_speed_label', 'feared_speed_increment', 'feared_speed_decrement', 'feared_speed_value',
                                    'collision_weight_label', 'collision_weight_increment', 'collision_weight_decrement', 'collision_weight_value']
        for v in self.object_edit_buttons:
            self.buttons[v].visible = False
            self.buttons[v].enabled = False

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

    def object_to_edit_selected(self, o):  # show object editing options when an object is selected
        self.object_to_edit = o
        if self.object_to_edit:
            self.buttons['feared_speed_value'].text = str(self.object_to_edit.feared_speed)
            self.buttons['normal_speed_value'].text = str(self.object_to_edit.normal_speed)
            self.buttons['collision_weight_value'].text = str(self.object_to_edit.collision_weight)
            for v in self.object_edit_buttons:
                self.buttons[v].visible = True
                self.buttons[v].enabled = True
        else:
            self.show_fears_checklist = False
            self.show_scared_of_checklist = False
            self.toggle_button_colour(self.buttons['scared_of_checklist_toggle'], 0)
            self.toggle_button_colour(self.buttons['fears_checklist_toggle'], 0)
            for v in self.object_edit_buttons:
                self.buttons[v].visible = False
                self.buttons[v].enabled = False
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
            for i, o in enumerate(t.objects):
                circ = graphics.draw_circle(25, self.trigger_display_colours[i])
                # circ.set_position(o.coord[0], o.coord[1])
                te = self.create_text_sprite(t.legend[i])  # font.render(t.legend[i], True, (255, 255, 255))
                # t.set_position(o.coord[0, o.coord[1]])
                self.trigger_display_circles.append((circ, o))
                self.trigger_display_text.append((te, o))

    def create_text_sprite(self, tex):
        if not tex in self.text_sprites.keys():
            self.text_sprites[tex] = text.new(text=tex, font_size=self.font_size, centered=True)
            self.text_sprites[tex].color = (200, 200, 200, 255)
        return self.text_sprites[tex]

    def display_trigger(self):
        self.draw_trigger(self.drop_lists['view_triggers'].selected)

    def create_trigger_cursor(self, tex):
        t = self.create_text_sprite(tex)
        self.game.cursor = Cursor(self.game, t)
        self.game.gather_buttons_and_drop_lists_and_objects()

    def new_trigger(self):
        if self.drop_lists['new_triggers'].selected:
            self.trigger_prototype = self.drop_lists['new_triggers'].selected()
            self.game.new_trigger_capture = True
            self.create_trigger_cursor(self.trigger_prototype.legend[0])

    def update_new_trigger(self, o):
        t = self.trigger_prototype
        l = t.objects
        if o in l:
            l.remove(o)
        else:
            l.append(o)

        target_number = len(self.trigger_prototype.legend)
        if len(l) == target_number:
            name = 0
            for n in self.game.map.triggers.keys():
                if isinstance(n, int):
                    if n >= name:
                        name = n + 1
            self.game.map.triggers[name] = self.drop_lists['new_triggers'].selected(*l)
            self.draw_trigger(None)
            self.game.cursor = None
            self.game.gather_buttons_and_drop_lists_and_objects()

            self.drop_lists['new_triggers'].selected = None
            self.drop_lists['new_triggers'].drop_buttons[0].perf_function()  # call the <None> function
            self.game.new_trigger_capture = False
            self.trigger_prototype = None

            self.drop_lists['view_triggers'].refresh()
        else:
            self.create_trigger_cursor(self.trigger_prototype.legend[len(l)])

            self.draw_trigger(t)


