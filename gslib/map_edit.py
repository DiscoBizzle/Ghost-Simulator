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


class Cursor(game_object.GameObject):
    def __init__(self, game, sprite):
        game_object.GameObject.__init__(self, game, 0, 0, 0, 0, None)
        # self.frame_rect = pygame.Rect((0, 0), surface.get_size())
        self.max_frames = 0
        # self.sprite_height = surface.get_height()
        # self.sprite_width = surface.get_width()
        self.current_speed = 0
        self.normal_speed = 0

        self.update = none

        self.sprite = sprite
        self.isCursor = True


class Editor(object):
    def __init__(self, game, pos=(0, 0)):
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

        self.buttons['pick_object_label'] = button.DefaultButton(self, None, pos=(100, GAME_HEIGHT - 20), text="Place Object")
        self.drop_lists['pick_object'] = drop_down_list.DropDownList(self, self.possible_characters,
                                                                     self.update_object_prototype, pos=(200, GAME_HEIGHT - 20))
        self.object_prototype = None

        ###################################################################
        # View existing Trigger
        ###################################################################

        self.buttons['view_triggers_label'] = button.DefaultButton(self, None, pos=(320, GAME_HEIGHT - 20), size=(120, 20),
                                                                   text="Current Triggers")
        self.drop_lists['view_triggers'] = drop_down_list.DropDownList(self, self.game.map.triggers,
                                                                       self.display_trigger, pos=(440, GAME_HEIGHT - 20),
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
        self.buttons['new_trigger_label'] = button.DefaultButton(self, None, pos=(760, GAME_HEIGHT - 20), size=(100, 20),
                                                                 text="New trigger")
        self.drop_lists['new_triggers'] = drop_down_list.DropDownList(self, self.possible_triggers,
                                                                      self.new_trigger, pos=(860, GAME_HEIGHT - 20),
                                                                      size=(300, 20))
        # self.new_trigger_objects = []
        self.trigger_prototype = None

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


