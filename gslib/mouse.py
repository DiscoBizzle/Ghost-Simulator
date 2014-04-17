import pygame

import character
from gslib.constants import *


class MouseController(object):
    def __init__(self, game):
        self.game = game
        self.interaction_this_click = False

    def mouse_click(self, pos, typ, button):
        self.interaction_this_click = False
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(pos, typ, button)
        elif self.game.GameState == MAIN_GAME:
            if not self.interaction_this_click:
                self.check_button_click(pos, typ, button)

            if not self.interaction_this_click:
                self.check_list_event(pos, typ, button)

            if not self.interaction_this_click:
                if self.game.editor_active:
                    self.editor_click(pos, typ, button)


            if not self.interaction_this_click:
                self.check_object_click(pos, typ, button)

        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(pos, typ, button)
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(pos, typ, button)
        elif self.game.GameState == KEYBIND_MENU:
            self.game.keybind_menu.mouse_event(pos, typ, button)

    def mouse_move(self, pos):
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(pos, 'move')
        elif self.game.GameState == MAIN_GAME:
            for k, v in self.game.drop_lists.iteritems():
                v.handle_event(pos, 'move')
            if self.game.cursor:
                self.calc_cursor_coord(pos, 'move')

        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(pos, 'move')
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(pos, 'move')

    def calc_cursor_coord(self, pos, typ, button=None):
        if self.game.key_controller.keys[self.game.key_controller.key_map['Snap to Grid']]:
            grid_x = (pos[0] + self.game.camera_coords[0]) / TILE_SIZE
            grid_y = (pos[1] + self.game.camera_coords[1]) / TILE_SIZE
            self.game.cursor.coord = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)

        else:
            self.game.cursor.coord = (pos[0] + self.game.camera_coords[0], pos[1] + self.game.camera_coords[1])

    def check_object_click(self, pos, typ, button=None):
        if typ == 'down':
            if pos[0] > LEVEL_WIDTH or pos[1] > LEVEL_HEIGHT:  # don't check for object outside of level area
                return
            for o_name, o in self.game.objects.iteritems():
                if o == self.game.cursor:
                    continue
                st = SELECTION_TOLERANCE
                temp_rect = pygame.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
                if temp_rect.collidepoint((pos[0]+self.game.camera_coords[0], pos[1]+self.game.camera_coords[1])) and isinstance(o, character.Character):

                    if self.game.new_trigger_capture:
                        self.game.editor.update_new_trigger(o_name)
                    else:
                        self.game.disp_object_stats = True
                        self.game.object_stats = o.info_sheet
                        self.game.selected_object = o
                        if self.game.editor_active:
                            self.game.editor.object_to_edit_selected(o)

                    self.interaction_this_click = True
                    return
            self.game.selected_object = None
            self.game.disp_object_stats = False
            self.game.object_stats = None
            self.game.editor.object_to_edit_selected(None)

    def check_button_click(self, pos, typ, mouse_button=None):
        if typ == 'up':
            return
        for button in self.game.buttons.itervalues():
            if button.check_clicked(pos):
                self.interaction_this_click = True

    def check_list_event(self, pos, typ, button=None):
        if typ == 'up':
            return
        for v in self.game.drop_lists.itervalues():
            if v.handle_event(pos, typ, button):
                self.interaction_this_click = True

    def editor_click(self, pos, typ, button=None):
        if typ == 'up':  # only detect mouse down
            return
        if pos[0] > self.game.dimensions[0] - self.game.camera_padding[1] or \
           pos[0] < self.game.camera_padding[0] or \
           pos[1] > self.game.dimensions[1] - self.game.camera_padding[3] or \
           pos[1] < self.game.camera_padding[2]:  # don't check outside of level area
            return
        # if cursor exists, and is an object prototype, create new object
        if self.game.editor.object_prototype and self.game.cursor == self.game.editor.object_prototype:
            obj_type = type(self.game.cursor)
            pos = self.game.cursor.coord
            name = self.game.cursor.__class__.__name__
            while True:
                if name in self.game.map.objects.keys():
                    name += '0'
                else:
                    break

            self.game.map.objects[name] = obj_type(self.game, x=pos[0], y=pos[1])
            self.game.gather_buttons_and_drop_lists_and_objects()
            self.interaction_this_click = True

        for name, o in self.game.map.objects.iteritems():
            print name, o

