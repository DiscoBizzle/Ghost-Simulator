try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

import pygame

from gslib.constants import *

# screen = pygame.display.set_mode((800, 800))
blue = pygame.Color(0, 255, 0)
black = pygame.Color(0, 0, 0)


class Graphics(object):
    def __init__(self, game):
        self.game = game
        self.surface = pygame.display.set_mode(self.game.dimensions)

        self.field = pygame.image.load(os.path.join(TILES_DIR, 'field.png'))
        self.field = pygame.transform.scale(self.field, (GAME_WIDTH, GAME_HEIGHT))
        self.field.set_alpha(100)
        self.field.convert_alpha()

        self.light = pygame.image.load(os.path.join(TILES_DIR, 'light.png'))
        self.light.convert_alpha()
        self.light = pygame.transform.scale(self.light, (200, 200))

    def draw_game_over(self):
        font = pygame.font.SysFont('helvetica', 80)
        size = font.size("GAME OVER")
        margin = (self.game.dimensions[0] - size[0]) / 2
        self.game.screen_objects_to_draw.append((font.render("GAME OVER", True, (255, 255, 255)), (margin, 100)))
    
        font = pygame.font.SysFont('helvetica', 20)
        size = font.size("press esc scrub")
        margin = (self.game.dimensions[0] - size[0]) / 2
        self.game.screen_objects_to_draw.append((font.render("press esc scrub", True, (255, 255, 255)), (margin, 200)))
    
    
    def main_game_draw(self):
        # this runs faster than game update. animation can be done here with no problems.
        if self.game.GameState != CUTSCENE:
            self.surface.fill(black)

        if self.game.GameState == STARTUP:
            pass
        elif self.game.GameState == MAIN_MENU:
            self.game.Menu.display()
        elif self.game.GameState == MAIN_GAME:
            self.draw_map()
            self.draw_objects()
            if self.game.options['torch']:
                self.draw_torch()

            self.draw_buttons()

            self.draw_fear_bar()
            self.draw_fps()
            self.draw_character_stats()
        elif self.game.GameState == GAME_OVER:
            self.draw_game_over()
        elif self.game.GameState == CREDITS:
            self.game.credits.display()
        elif self.game.GameState == SKILLS_SCREEN:
            self.game.SkillMenu.display()
        elif self.game.GameState == OPTIONS_MENU:
            self.game.options_menu.display()
        elif self.game.GameState == TEXTBOX_TEST:
            self.draw_text_box()

        if not self.game.options['FOV']:
            self.screen_objects_to_draw = []
            self.world_objects_to_draw = []

        self.draw_world_objects()
        self.draw_screen_objects()

        if self.game.options['VOF'] and self.game.GameState != CUTSCENE:
            self.surface.blit(self.field, (0, 0))

        pygame.display.update()
    
    
    def draw_map(self):
        m = self.game.map
        grid_size = TILE_SIZE
        nw = len(m.grid)
        nh = len(m.grid[0])
        if not hasattr(self.game, 'map_surf'):
            self.game.map_surf = pygame.Surface((nw * grid_size, nh * grid_size)).convert()
        surf = self.game.map_surf
    
        clippy = self.game.clip_area.copy() if hasattr(self.game, 'clip_area') else pygame.Rect((0, 0), (GAME_WIDTH, GAME_HEIGHT))
        clippy.inflate_ip(64, 64)
    
        for i in range(nw):
            for j in range(nh):
                area = m.grid[i][j].tileset_area
                if clippy.colliderect(pygame.Rect((i * grid_size, j * grid_size), (grid_size, grid_size))):
                    surf.blit(m.tileset, (i * grid_size, j * grid_size), area)
    
                ##TEMPORARY - DRAWS SOLID TILES FOR COLLISION DEBUG
                #if not m.grid[i][j].walkable:
                #    temprect = pygame.Rect(i * grid_size, j * grid_size, TILE_SIZE, TILE_SIZE)
                #    pygame.draw.rect(surf, 0x0000ff, temprect)
    
        self.game.world_objects_to_draw = [(surf, (0, 0))] + self.game.world_objects_to_draw
    
    
    def draw_fps(self):
        font = pygame.font.SysFont('helvetica', 20)
        surf = font.render(u'FPS: ' + unicode(int(self.game.fps_clock.get_fps())), True, (255, 255, 0))
        self.game.screen_objects_to_draw.append((surf, (0, self.game.dimensions[1] - 100)))
    
    
    def draw_buttons(self):
        for button in self.game.buttons.itervalues():
            self.game.screen_objects_to_draw.append((button.surface, button.pos))
    
    
    def draw_objects(self):
        self.game.objects.sort((lambda x, y: cmp(x.coord[1], y.coord[1])))
        for o in self.game.objects:
            if o == self.game.player1:
                if o.possessing:
                    continue
            surf = pygame.Surface((SPRITE_WIDTH, SPRITE_HEIGHT))
            surf.fill((255, 0, 255))
            surf.blit(o.sprite_sheet, (0, 0), o.frame_rect)
            surf.set_colorkey((255, 0, 255))
            self.game.world_objects_to_draw.append((surf, (o.coord[0] + o.dimensions[0] - SPRITE_WIDTH, o.coord[1] + o.dimensions[1] - SPRITE_HEIGHT)))
    
    
    def draw_character_stats(self):
        if self.game.disp_object_stats:
            self.game.screen_objects_to_draw.append((self.game.object_stats[0], self.game.object_stats[1]))
    
    
    def draw_fear_bar(self):
        if not hasattr(self.game, 'fear_txt'):
            font = pygame.font.SysFont('helvetica', 20)
            self.game.fear_size = font.size(u"FEAR")
            self.game.fear_txt = font.render(u"FEAR", True, (200, 200, 200)).convert_alpha()
    
        if not hasattr(self.game, 'fear_surf'):
            self.game.fear_surf = pygame.Surface((self.game.dimensions[0], 32)).convert_alpha()
    
        surf = self.game.fear_surf
        surf.blit(self.game.fear_txt, (0, 0))
        pygame.draw.rect(surf, (255, 0, 0), pygame.Rect((self.game.fear_size[0], 0), ((self.game.dimensions[0] - self.game.fear_size[0]) * (self.game.player1.fear/float(MAX_FEAR)), 32)))
        self.game.screen_objects_to_draw.append((surf, (0, self.game.dimensions[1] - 32)))
    
    
    def draw_world_objects(self):  # stuff relative to camera
        for f in self.game.world_objects_to_draw:
            self.blit_camera(f[0], f[1])
        self.game.world_objects_to_draw = []
    
    
    def draw_screen_objects(self):  # stuff relative to screen
        for f in self.game.screen_objects_to_draw:
            self.blit(f[0], f[1])
        self.game.screen_objects_to_draw = []
    
    
    def blit(self, surf, pos):
        self.surface.blit(surf, pos)
    
    
    def blit_camera(self, surf, pos):
        cpos = (pos[0] - self.game.camera_coords[0], pos[1] - self.game.camera_coords[1])
        self.surface.blit(surf, cpos)
    
    def draw_cutscene(self):
        #print game.cutscene_started
        #print hasattr(game, 'movie')
        #print game.GameState
    
        if self.game.cutscene_started and hasattr(self.game, 'movie'):
            if not self.game.movie.get_busy():
                self.game.GameState = MAIN_GAME
                self.game.cutscene_started = False
                self.game.clock.get_time()  # hack required for pygame.game.movie linux
                del self.game.movie  # hack required for pygame.movie mac os x
        else:
            self.surface.fill(pygame.Color(0, 0, 0))
            pygame.display.update()
            try:
                f = BytesIO(open(self.game.cutscene_next, "rb").read())
                self.game.movie = pygame.movie.Movie(f)
                w, h = self.game.movie.get_size()
                self.game.movie.play()
                self.game.cutscene_started = True
            except IOError:
                print u"Video not found: " + self.game.cutscene_next
                self.game.GameState = MAIN_MENU
    
    
    def draw_torch(self):
        ppos = (self.game.player1.coord[0] + self.game.player1.dimensions[0] / 2, self.game.player1.coord[1] + self.game.player1.dimensions[1] / 2)
    
        light_size = self.light.get_size()
        if not hasattr(self.game, 'hole_surf'):
            self.game.hole_surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert_alpha()
        surf = self.game.hole_surf
        surf.fill((0, 0, 0, 0))
    
        hole = pygame.Rect((ppos[0] - light_size[0]/2 - self.game.camera_coords[0], ppos[1] - light_size[1]/2 - self.game.camera_coords[1]), light_size)
        if hasattr(self.game, 'clip_area'):
            self.game.old_clip_area = self.game.clip_area
        self.game.clip_area = hole
    
        pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((0, 0), (GAME_WIDTH, hole.top)))
        pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((0, 0), (hole.left, GAME_HEIGHT)))
        pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((hole.right, 0), (GAME_WIDTH, GAME_HEIGHT)))
        pygame.draw.rect(surf, (0, 0, 0, 255), pygame.Rect((0, hole.bottom), (GAME_WIDTH, GAME_HEIGHT)))
        self.game.screen_objects_to_draw.append((surf, (0, 0)))
        self.game.world_objects_to_draw.append((self.light, (ppos[0] - light_size[0]/2, ppos[1] - light_size[1]/2)))
    
    
    def draw_text_box(self):
        self.surface.blit(self.game.text_box_test.background_surface, (0, 0))
        self.game.text_box_test.create_text_surface()
        self.surface.blit(self.game.text_box_test.text_surface, (self.game.text_box_test.text_frame_rect.x, self.game.text_box_test.text_frame_rect.y))
