import pygame

import character
from gslib.constants import *


class MouseController(object):
    def __init__(self, game):
        self.game = game
        self.interaction_this_click = False

    def mouse_click(self, event):
        self.interaction_this_click = False
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(event)
        elif self.game.GameState == MAIN_GAME:
            if not self.interaction_this_click:
                self.check_button_click(event)

            if not self.interaction_this_click:
                self.check_object_click(event)

            for k, v in self.game.drop_lists.iteritems():
                if not self.interaction_this_click:
                    self.interaction_this_click = v.handle_event(event)

            if not self.interaction_this_click:
                if self.game.editor_active:
                    self.editor_click(event)

        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(event)
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(event)
        elif self.game.GameState == KEYBIND_MENU:
            self.game.keybind_menu.mouse_event(event)

    def mouse_up(self, event):
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(event)
        elif self.game.GameState == MAIN_GAME:
            pass
        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(event)
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(event)

    def mouse_move(self, event):
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(event)
        elif self.game.GameState == MAIN_GAME:
            for k, v in self.game.drop_lists.iteritems():
                v.handle_event(event)
            if self.game.cursor:
                self.calc_cursor_coord(event)

        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(event)
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(event)

    def calc_cursor_coord(self, event):
        if self.game.key_controller.keys[self.game.key_controller.key_map['Snap to Grid']]:
            grid_x = (event.pos[0] + self.game.camera_coords[0] + self.game.camera_padding[0]) / TILE_SIZE
            grid_y = (event.pos[1] + self.game.camera_coords[1] + self.game.camera_padding[2]) / TILE_SIZE
            self.game.cursor.coord = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)

        else:
            self.game.cursor.coord = (event.pos[0] + self.game.camera_coords[0], event.pos[1] + self.game.camera_coords[1])

    def check_object_click(self, event):
        if event.pos[0] > LEVEL_WIDTH or event.pos[1] > LEVEL_HEIGHT:  # don't check for object outside of level area
            return
        for o in self.game.objects.itervalues():
            if o == self.game.cursor:
                continue
            st = SELECTION_TOLERANCE
            temp_rect = pygame.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
            if temp_rect.collidepoint((event.pos[0]+self.game.camera_coords[0],event.pos[1]+self.game.camera_coords[1])) and isinstance(o, character.Character):
                self.game.disp_object_stats = True
                self.game.object_stats = (o.info_sheet, (self.game.dimensions[0] - o.info_sheet.get_width(), 0))
                self.game.selected_object = o

                if self.game.new_trigger_capture:
                    self.game.editor.update_new_trigger(o)
                    # self.new_trigger_object_capture(o)

                self.interaction_this_click = True
                return
        self.game.selected_object = None
        self.game.disp_object_stats = False
        self.game.object_stats = None

    def check_button_click(self, event):
        for button in self.game.buttons.itervalues():
            self.interaction_this_click = button.check_clicked(event.pos)

    # def new_trigger_object_capture(self, o):
    #     l = self.game.editor.new_trigger_objects
    #     if o in l:
    #         l.remove(o)
    #     else:
    #         l.append(o)

    def editor_click(self, event):
        if event.pos[0] > self.game.dimensions[0] - self.game.camera_padding[1] or \
           event.pos[0] < self.game.camera_padding[0] or \
           event.pos[1] > self.game.dimensions[1] - self.game.camera_padding[3] or \
           event.pos[1] < self.game.camera_padding[2]:  # don't check outside of level area
            return
        if self.game.editor.object_prototype and self.game.cursor == self.game.editor.object_prototype:
            obj_type = type(self.game.cursor)
            pos = self.game.cursor.coord
            name = 0
            for n in self.game.map.objects.keys():
                if isinstance(n, int):
                    if n >= name:
                        name = n + 1
            self.game.map.objects[name] = obj_type(self.game, x=pos[0], y=pos[1])
            self.game.gather_buttons_and_drop_lists_and_objects()
            self.interaction_this_click = True

