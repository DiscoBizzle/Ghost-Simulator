import pygame

import character
from gslib.constants import *


class MouseController(object):
    def __init__(self, game):
        self.game = game
        self.interaction_this_click = False
        self.button_to_click = None
        self.game.window.push_handlers(self)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_move((x, y))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_move((x, y))

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_click((x, y), 'down', button)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_click((x, y), 'up', button)

    def mouse_click(self, pos, typ, button):
        self.interaction_this_click = False
        if self.game.state == MAIN_GAME:
            self.button_to_click = None
            if not self.interaction_this_click:
                self.check_button_click(pos, typ, button)

            if not self.interaction_this_click:
                self.check_list_event(pos, typ, button)
            # if not self.interaction_this_click:
            #     self.check_list_and_button_click(pos, typ, button)

            # if self.button_to_click:
            #     self.button_to_click.perf_function()

            if not self.interaction_this_click:
                if self.game.editor_active:
                    self.editor_click(pos, typ, button)


            if not self.interaction_this_click:
                self.check_object_click(pos, typ, button)

    def mouse_move(self, pos):
        if self.game.state == MAIN_GAME:
            for k, v in dict(self.game.drop_lists, **self.game.editor.get_lists() if self.game.editor_active else {}).iteritems():
                v.handle_event(pos, 'move')
            if self.game.cursor:
                self.calc_cursor_coord(pos, 'move')

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
                if temp_rect.collidepoint((pos[0]+self.game.camera_coords[0], pos[1]+self.game.camera_coords[1])):

                    if self.game.new_trigger_capture:
                        self.game.editor.update_new_trigger(o_name)
                    elif isinstance(o, character.Character):
                        self.game.disp_object_stats = True
                        self.game.object_stats = o.info_sheet
                        self.game.selected_object = o
                        if self.game.editor_active:
                            self.game.editor.object_to_edit_selected(o_name)

                    self.interaction_this_click = True
                    return
            self.game.selected_object = None
            self.game.disp_object_stats = False
            self.game.object_stats = None
            self.game.editor.object_to_edit_selected(None)

    def check_button_click(self, pos, typ, mouse_button=None):
        if typ == 'up':
            return
        to_click = None
        for button in dict(self.game.buttons, **self.game.editor.get_buttons() if self.game.editor_active else {}).itervalues():
            if button.check_clicked_no_function(pos):
                to_click = button
                if button.priority:
                    break
        if to_click:
            self.interaction_this_click = True
            # self.button_to_click = to_click
            if self.game.editor_active and not (to_click.text == "Undo" or to_click.text == "Redo"):
                self.game.editor.create_undo_state()
            to_click.perf_function()
            # if button.check_clicked(pos):
            #     self.interaction_this_click = True

    def check_list_event(self, pos, typ, button=None):
        if typ == 'up':
            return
        to_click = None
        for v in dict(self.game.drop_lists, **self.game.editor.get_lists() if self.game.editor_active else {}).itervalues():
            if v.check_click_within_area(pos):
                to_click = v
                if hasattr(v, 'priority') and v.priority:
                    break
        if to_click:
            if self.game.editor_active:
                self.game.editor.create_undo_state()
            if to_click.handle_event(pos, typ, button):
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

            self.game.editor.create_undo_state()

