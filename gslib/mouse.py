import pygame

import character
from gslib.constants import *

class MouseController(object):
    def __init__(self, game):
        self.game = game

    def mouse_click(self, event):
        if self.game.GameState == MAIN_MENU:
            self.game.Menu.mouse_event(event)
        elif self.game.GameState == MAIN_GAME:
            self.check_button_click(event)
            self.check_object_click(event)
        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.mouse_event(event)
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(event)

    def mouse_up(self, event):
        if self.game.GameState == MAIN_MENU:
            pass
        elif self.game.GameState == MAIN_GAME:
            pass
        elif self.game.GameState == SKILLS_SCREEN:
            pass
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(event)

    def mouse_move(self, event):
        if self.game.GameState == MAIN_MENU:
            pass
        elif self.game.GameState == MAIN_GAME:
            pass
        elif self.game.GameState == SKILLS_SCREEN:
            pass
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.mouse_event(event)

    def check_object_click(self, event):
        if event.pos[0] > LEVEL_WIDTH or event.pos[1] > LEVEL_HEIGHT: # make track camera
            return
        for o in self.game.objects:
            st = SELECTION_TOLERANCE
            temp_rect = pygame.Rect((o.coord[0] - st, o.coord[1] - st), (o.dimensions[0] + 2*st, o.dimensions[1] + 2*st))
            if temp_rect.collidepoint((event.pos[0]+self.game.camera_coords[0],event.pos[1]+self.game.camera_coords[1])) and isinstance(o, character.Character):
                self.game.disp_object_stats = True
                self.game.object_stats = (o.info_sheet, (GAME_WIDTH - o.info_sheet.get_width(), 0))
                if self.game.player1.possessing:
                    return
                self.game.toPossess = o
                self.game.buttons['Possess'].visible = True
                # self.buttons['Possess'].enabled = True
                self.game.buttons['Possess'].pos = (GAME_WIDTH - o.info_sheet.get_width(), o.info_sheet.get_height())
                self.game.buttons['unPossess'].pos = (GAME_WIDTH - o.info_sheet.get_width(), o.info_sheet.get_height())
                return
        self.game.disp_object_stats = False
        self.game.object_stats = None
        self.game.buttons['Possess'].visible = False
        self.game.buttons['Possess'].enabled = False

    def check_button_click(self, event):
        for button in self.game.buttons.itervalues():
            button.check_clicked(event.pos)

        if self.game.player1.possessing:
            self.game.buttons['Possess'].visible = False
            self.game.buttons['Possess'].enabled = False
            self.game.buttons['unPossess'].visible = True
            self.game.buttons['unPossess'].enabled = True
        else:
            self.game.buttons['Possess'].visible = True
            self.game.buttons['Possess'].enabled = True
            self.game.buttons['unPossess'].visible = False
            self.game.buttons['unPossess'].enabled = False
