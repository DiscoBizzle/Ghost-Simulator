from __future__ import absolute_import, division, print_function

import pyglet

from gslib.constants import *
from gslib.engine import rect
from gslib.game_objects import character
from gslib import window


class MouseController(object):
    def __init__(self, game):
        self.game = game
        self.interaction_this_click = False
        self.button_to_click = None
        window.push_handlers(self)

        self.object_capture_request = False
        self.object_capture_function = None

        self.position_capture_request = False
        self.position_capture_function = None

        self.mouse_motion_capture_request = False
        self.mouse_motion_capture_function = None

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

    def pick_position(self, func, typ='down', button=pyglet.window.mouse.LEFT, relative_to_map=True):
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

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_move((x, y))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_move((x, y))

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_click((x, y), 'down', button)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_click((x, y), 'up', button)

    def on_mouse_scroll(self, x, y, dx, dy):
        self.game.zoom += dy / 10

    def mouse_click(self, pos, typ, button):
        self.interaction_this_click = False
        if self.game.state == MAIN_GAME or self.game.state == EDITOR:
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

            if not self.interaction_this_click and button == pyglet.window.mouse.LEFT:
                self.check_object_click(pos, typ, button)

            if not self.interaction_this_click and button == pyglet.window.mouse.RIGHT:
                self.check_navigation_click(pos, typ, button)

    def mouse_move(self, pos):
        if self.game.state == MAIN_GAME or self.game.state == EDITOR:
            if self.game.message_box:
                return
            if self.game.cursor:
                self.game.cursor.coord = self.calc_cursor_coord(pos, 'move')

            if self.mouse_motion_capture_request:
                self.mouse_motion_capture_request = False
                self.mouse_motion_capture_function(pos)

    def calc_cursor_coord(self, pos, typ, button=None):
        if self.game.key_controller.keys[self.game.key_controller.key_map['Snap to Grid']]:
            grid_x, grid_y = self.game.camera.undo_camera(pos)
            return (grid_x // TILE_SIZE) * TILE_SIZE, (grid_y // TILE_SIZE) * TILE_SIZE
        else:
            return self.game.camera.undo_camera(pos)

    def check_object_click(self, pos, typ, button=None):
        if typ == 'down':
            if pos[0] > LEVEL_WIDTH or pos[1] > LEVEL_HEIGHT:  # don't check for object outside of level area
                return
            for o_name, o in self.game.objects.iteritems():
                if o == self.game.cursor:
                    continue
                st = SELECTION_TOLERANCE
                temp_rect = rect.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
                if temp_rect.collidepoint(self.game.camera.undo_camera(pos)):

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

    def check_navigation_click(self, pos, typ, button=None):
        if typ == 'down':
            start_t = self.game.players['player1'].coord
            start_t = (start_t[0] // TILE_SIZE, start_t[1] // TILE_SIZE)
            goal_t = self.game.camera.undo_camera(pos)
            goal_t = (goal_t[0] // TILE_SIZE, goal_t[1] // TILE_SIZE)
            path = self.game.pathfinder.get_path(start_t, goal_t, 1, 100)
            # cheat; pretend we're not tile-based...
            if path is not None:
                # ignore start b/c we're already there
                path.pop(0)
                # make end coords we clicked on
                goal_t = self.game.camera.undo_camera(pos)
                path[len(path) - 1] = (goal_t[0] / TILE_SIZE, goal_t[1] / TILE_SIZE)
                # TODO: more post-processing. move inside pathfinder? probably a good idea.
            self.game.players['player1'].path = path or []
            print(path)
            self.interaction_this_click = True

    def editor_click(self, pos, typ, button=None):
        if typ == 'up':  # only detect mouse down
            return
        x, y = self.calc_cursor_coord(pos, typ, button=button)
        # don't check outside of level area
        if x < 0 or x >= LEVEL_WIDTH or y < 0 or y >= LEVEL_HEIGHT:
            return
        # if cursor exists, and is an object prototype, create new object
        if self.game.editor.object_prototype and self.game.cursor == self.game.editor.object_prototype:
            # obj_type = type(self.game.cursor)
            name = self.game.cursor.__class__.__name__
            while True:
                if name in self.game.map.objects.keys():
                    name += '0'
                else:
                    break

            dic = self.game.editor.object_prototype.create_save_dict()
            ch = character.Character(self.game, 0, 0, 32, 32)
            ch.load_from_dict(dic)

            self.game.map.objects[name] = ch
            self.game.gather_buttons_and_drop_lists_and_objects()
            self.interaction_this_click = True

            self.game.editor.create_undo_state()
