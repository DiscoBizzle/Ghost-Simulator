import character
from gslib.constants import *
from gslib import rect
import pyglet

class MouseController(object):
    def __init__(self, game):
        self.game = game
        self.interaction_this_click = False
        self.button_to_click = None
        self.game.window.push_handlers(self)

        self.object_capture_request = False
        self.object_capture_function = None

        self.position_capture_request = False
        self.position_capture_function = None

    def pick_object(self, func, return_object=False):
        """
            Pass in function to receive picked object_name as sole argument
            OR set return_object=True, then the actual object is returned as sole argument
        """
        self.object_capture_request = True

        if not return_object:
            self.object_capture_function = func
        else:
            def f(o_name):
                obj = self.game.objects[o_name]
                func(obj)
            self.object_capture_function = f

    def pick_position(self, func, typ='down', button=MOUSE_LEFT, relative_to_map=True):
        """
        Pass in a function to receive picked position (x, y) as sole argument
        if relative_to_map=True: Returns cursor coordinate (i.e. relative to actual game map) (Supports snap-to-grid)
        checks if typ (up or down) and button(left, right, middle) are correct. Set button=MOUSE_LEFT etc.
        """
        self.position_capture_request = True

        if not relative_to_map:
            def f(pos, typp, buttonn):
                if not typp == typ or not button == buttonn: # dont capture wrong type of click (i.e. down instead of up)
                    self.position_capture_request = True # allow capture of next click too
                    return
                func(pos)
                self.interaction_this_click = True
            self.position_capture_function = f
        else:
            def f(pos, typp, buttonn):
                if not typp == typ or not button == buttonn: # dont capture wrong type of click (i.e. down instead of up)
                    self.position_capture_request = True # allow capture of next click too
                    return
                n_pos = self.calc_cursor_coord(pos, typp, button)
                func(n_pos)
                self.interaction_this_click = True
            self.position_capture_function = f

    def post_to_text_caret(self, fun_name, *args):
        # post copy to text editor if set. don't overlap the text editor with usable controls!
        # (input message boxes get away with it because they disable all non-msgbox controls.)
        if self.game.text_caret is not None and hasattr(self.game.text_caret, fun_name):
            getattr(self.game.text_caret, fun_name)(*args)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_move((x, y))
        self.post_to_text_caret('on_mouse_motion', x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_move((x, y))
        self.post_to_text_caret('on_mouse_drag', x, y, dx, dy, buttons, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_click((x, y), 'down', button)
        self.post_to_text_caret('on_mouse_press', x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_click((x, y), 'up', button)
        self.post_to_text_caret('on_mouse_release', x, y, button, modifiers)

    def mouse_click(self, pos, typ, button):
        self.interaction_this_click = False
        if self.game.state == MAIN_GAME or self.game.state == EDITOR:

            if not self.interaction_this_click:
                self.check_button_click(pos, typ, button)

            if not self.interaction_this_click:
                self.check_list_event(pos, typ, button)

            if not self.interaction_this_click and self.position_capture_request:
                self.position_capture_request = False
                self.position_capture_function(pos, typ, button)

            if not self.interaction_this_click:
                if self.game.state == EDITOR:
                    self.editor_click(pos, typ, button)

            if not self.interaction_this_click and typ == 'down':
                if self.game.state == EDITOR:
                    # TODO: take into account camera coordinates
                    self.interaction_this_click = self.game.editor.handle_map_click(pos)

            if not self.interaction_this_click:
                self.check_object_click(pos, typ, button)

    def mouse_move(self, pos):
        if self.game.state == MAIN_GAME or self.game.state == EDITOR:
            if self.game.message_box:
                return
            for k, v in dict(self.game.drop_lists, **self.game.editor.get_lists() if self.game.state == EDITOR else {}).iteritems():
                v.handle_event(pos, 'move')
            if self.game.cursor:
                self.game.cursor.coord = self.calc_cursor_coord(pos, 'move')

    def calc_cursor_coord(self, pos, typ, button=None):
        if self.game.key_controller.keys[self.game.key_controller.key_map['Snap to Grid']]:
            grid_x = (pos[0] + self.game.camera_coords[0]) / TILE_SIZE
            grid_y = (pos[1] + self.game.camera_coords[1]) / TILE_SIZE
            return grid_x * TILE_SIZE, grid_y * TILE_SIZE
        else:
            return pos[0] + self.game.camera_coords[0], pos[1] + self.game.camera_coords[1]

    def check_object_click(self, pos, typ, button=None):
        if typ == 'down':
            if pos[0] > LEVEL_WIDTH or pos[1] > LEVEL_HEIGHT:  # don't check for object outside of level area
                return
            for o_name, o in self.game.objects.iteritems():
                if o == self.game.cursor:
                    continue
                st = SELECTION_TOLERANCE
                temp_rect = rect.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
                if temp_rect.collidepoint((pos[0]+self.game.camera_coords[0], pos[1]+self.game.camera_coords[1])):

                    if self.object_capture_request:
                        self.object_capture_request = False
                        self.object_capture_function(o_name)
                    elif isinstance(o, character.Character):
                        self.game.disp_object_stats = True
                        self.game.object_stats = o.info_sheet
                        self.game.selected_object = o
                        if self.game.state == EDITOR:
                            self.game.editor.handle_object_click(o_name)

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
        if self.game.message_box is not None:
            for button in self.game.message_box.buttons:
                if button.check_clicked_no_function(pos):
                    to_click = button
            self.interaction_this_click = True  # never continue checking when message box is up
        else:
            for button in dict(self.game.buttons, **self.game.editor.get_buttons() if self.game.state == EDITOR else {}).itervalues():
                if button.check_clicked_no_function(pos):
                    to_click = button
                    if button.priority:
                        break
        if to_click:
            self.interaction_this_click = True
            # self.button_to_click = to_click
            if self.game.state == EDITOR and not (to_click.text == "Undo" or to_click.text == "Redo") and not self.game.message_box:
                self.game.editor.create_undo_state()
            to_click.perf_function()
            # if button.check_clicked(pos):
            #     self.interaction_this_click = True

    def check_list_event(self, pos, typ, button=None):
        if typ == 'up':
            return
        to_click = None
        for v in dict(self.game.drop_lists, **self.game.editor.get_lists() if self.game.state == EDITOR else {}).itervalues():
            if v.check_click_within_area(pos):
                to_click = v
                if hasattr(v, 'priority') and v.priority:
                    break
        if to_click:
            if self.game.state == EDITOR:
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

