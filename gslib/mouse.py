import pygame

import character
from gslib.constants import *

class MouseController(object):
    def __init__(self, game):
        self.game = game

    def mouse_click(self, pos, typ, button):
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(pos, typ, button)
        elif self.game.GameState == MAIN_GAME:
            self.check_button_click(pos, typ, button)
            self.check_object_click(pos, typ, button)
        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(pos, typ, button)
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(pos, typ, button)
        elif self.game.GameState == KEYBIND_MENU:
            self.game.keybind_menu.mouse_event(pos, typ, button)

    # def mouse_up(self, event):
    #     if self.game.GameState == MAIN_MENU:
    #         self.game.Menu.mouse_event(event)
    #     elif self.game.GameState == MAIN_GAME:
    #         pass
    #     elif self.game.GameState == SKILLS_SCREEN:
    #         self.game.SkillMenu.mouse_event(event)
    #     elif self.game.GameState == OPTIONS_MENU:
    #         self.game.options_menu.mouse_event(event)

    def mouse_move(self, pos):
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(pos, 'move')
        elif self.game.GameState == MAIN_GAME:
            pass
        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(pos, 'move')
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(pos, 'move')

    def check_object_click(self, pos, typ, button=None):
        if pos[0] > LEVEL_WIDTH or pos[1] > LEVEL_HEIGHT:  # don't check for object outside of level area
            return
        for o in self.game.objects.itervalues():
            st = SELECTION_TOLERANCE
            temp_rect = pygame.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
            if temp_rect.collidepoint((pos[0]+self.game.camera_coords[0], pos[1]+self.game.camera_coords[1])) and isinstance(o, character.Character):
                self.game.disp_object_stats = True
                self.game.object_stats = (o.info_sheet, (self.game.dimensions[0] - o.info_sheet[1].width, 0))
                self.game.selected_object = o

                return
        self.game.selected_object = None
        self.game.disp_object_stats = False
        self.game.object_stats = None

    def check_button_click(self, pos, typ, button=None):
        for button in self.game.buttons.itervalues():
            button.check_clicked(pos)

