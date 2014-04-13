try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

import pygame
import pyglet.image

from gslib.constants import *
from gslib import player
from gslib import sprite

import time

# screen = pygame.display.set_mode((800, 800))
blue = pygame.Color(0, 255, 0)
black = pygame.Color(0, 0, 0)

rect_tex = None
def new_rect_sprite():
    global rect_tex
    if rect_tex is None:
        rect_tex = pyglet.image.SolidColorImagePattern((255, 255, 255, 255)).create_image(1, 1).get_texture()
    return sprite.Sprite(rect_tex)

def draw_circle(r, colour, thickness):
    surf = pygame.Surface((r*2, r*2))
    surf.set_colorkey((0, 0, 0))
    pygame.draw.circle(surf, colour, (r, r), r, thickness)
    return surf


class Graphics(object):
    """
    see Game class for how to add things to be drawn.
    """
    def __init__(self, game):
        self.game = game
        #self.surface = pygame.display.set_mode(self.game.dimensions, pygame.RESIZABLE)

        self.field = sprite.Sprite(pyglet.image.load(os.path.join(TILES_DIR, 'field.png')).get_texture())
        self.field.scale_x = self.game.dimensions[0] / self.field.image.width
        self.field.scale_y = self.game.dimensions[1] / self.field.image.height

        self.light = sprite.Sprite(pyglet.image.load(os.path.join(TILES_DIR, 'light.png')).get_texture())
        self.light.scale_x = self.light.scale_y = (200.0 / self.light.image.height)
        self.light_size = (self.light.width, self.light.height)

        #font = pygame.font.SysFont(FONT, 20)
        #self.fear_size = font.size(u"FEAR")
        #self.fear_txt = font.render(u"FEAR", True, (200, 200, 200)).convert_alpha()
        #self.fear_surf = pygame.Surface((self.game.dimensions[0], 32)).convert_alpha()

        #font = pygame.font.SysFont(FONT, 80)
        #self.game_over_txt1_size = font.size(u"GAME OVER")
        #self.game_over_txt1 = font.render(u"GAME OVER", True, (255, 255, 255))

        #font = pygame.font.SysFont(FONT, 20)
        #self.game_over_txt2_size = font.size(u"press esc scrub")
        #self.game_over_txt2 = font.render(u"press esc scrub", True, (255, 255, 255))

        self.clip_area = pygame.Rect((0, 0), (self.game.dimensions[0], self.game.dimensions[1]))

        self.last_map = None
        self.map_texture = None
        self.tile_sprite = None

    def resize_window(self, event):
        print('TODO: graphics.resize_window() pyglet')
        return
        self.game.dimensions = event.size
        self.surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        self.clip_area = pygame.Rect((0, 0), (self.game.dimensions[0], self.game.dimensions[1]))

    def draw_game_over(self):
        margin = (self.game.dimensions[0] - self.game_over_txt1_size[0]) / 2
        self.game.screen_objects_to_draw.append((self.game_over_txt1, (margin, 100)))

        margin = (self.game.dimensions[0] - self.game_over_txt2_size[0]) / 2
        self.game.screen_objects_to_draw.append((self.game_over_txt2, (margin, 200)))
    
    def main_game_draw(self):
        # this runs faster than game update. animation can be done here with no problems.
        if self.game.GameState != CUTSCENE:
            self.game.clear()

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
        elif self.game.GameState == KEYBIND_MENU or self.game.GameState == KEYBIND_CAPTURE:
            self.game.keybind_menu.display()

        if self.game.options['FOV']:
            self.draw_world_objects()
            self.draw_screen_objects()

        if self.game.options['VOF'] and self.game.GameState != CUTSCENE:
            self.surface.blit(self.field, (0, 0))

    def draw_map(self):
        m = self.game.map

        if self.last_map is None or self.last_map != m:
            print('Redrawing map...')
            start_time = time.clock()
            if self.map_texture is not None:
                self.map_texture.delete()

            grid_size = TILE_SIZE

            self.map_texture = pyglet.image.Texture.create(grid_size * len(m.grid), grid_size * len(m.grid[0]))
            self.tile_sprite = sprite.Sprite(self.map_texture)

            nw = len(m.grid)
            nh = len(m.grid[0])

            for i in range(nw):
                for j in range(nh):
                    (a, b, k, l) = m.grid[i][j].tileset_area
                    tile_region = m.tileset.get_region(a, m.tileset.height - b - grid_size, k, l)
                    self.map_texture.blit_into(tile_region, i * grid_size, j * grid_size, 0)

                ##TEMPORARY - DRAWS SOLID TILES FOR COLLISION DEBUG
                #if not m.grid[i][j].walkable:
                #    temprect = pygame.Rect(i * grid_size, j * grid_size, TILE_SIZE, TILE_SIZE)
                #    pygame.draw.rect(surf, 0x0000ff, temprect)

            self.last_map = m

            print('Map redraw complete (took ' + str(time.clock() - start_time) + 's)')

        self.game.world_objects_to_draw.insert(0, self.tile_sprite)
        return self.tile_sprite

    def draw_buttons(self):
        for button in self.game.buttons.itervalues():
            self.game.screen_objects_to_draw.append(button.outer_sprite)
            self.game.screen_objects_to_draw.append(button.inner_sprite)
            self.game.screen_objects_to_draw.append(button.text_sprite)

    def draw_objects(self):
        sort_objs = self.game.objects.values()
        sort_objs.sort((lambda x, y: cmp(-x.coord[1], -y.coord[1])))

        for o in sort_objs:  # self.game.objects:
            if isinstance(o, player.Player): #o == self.game.player1:
                if o.possessing:
                    continue

            texture = o.sprite_sheet.get_region(o.frame_rect.x, o.frame_rect.y, o.sprite_width, o.sprite_height)
            object_sprite = sprite.Sprite(texture)
            x = o.coord[0] + o.dimensions[0] - o.sprite_width
            y = o.coord[1] + o.dimensions[1] - o.sprite_height

            object_sprite.set_position(x, y)
            self.game.world_objects_to_draw.append(object_sprite)

            for s, p in o.flair.itervalues():
                flair_sprite = sprite.Sprite(s)
                flair_sprite.set_position(x + p[0] + object_sprite.width / 2, y + p[1] + object_sprite.height / 2)
                self.game.world_objects_to_draw.append(flair_sprite)

            if o == self.game.selected_object:
                r = o.highlight_radius
                print('TODO draw_objects selected object circle')
                #surf = draw_circle(r, (200, 200, 200), 2)
                #pos = (o.coord[0] + o.dimensions[0]/2 - r, o.coord[1] + o.dimensions[0]/2 - r)
                #self.game.world_objects_to_draw.append((surf, pos))

    def draw_character_stats(self):
        return
        if self.game.disp_object_stats:
            self.game.screen_objects_to_draw.append((self.game.object_stats[0], self.game.object_stats[1]))

    def resize_fear_surface(self):
        nplayers = len(self.game.players)
        self.fear_surf = pygame.Surface((self.game.dimensions[0], nplayers*32)).convert_alpha()

    def draw_fear_bar(self):
        return
        nplayers = len(self.game.players)
        if nplayers > 1:
            self.resize_fear_surface()
        self.fear_surf.fill(black)
        self.fear_surf.blit(self.fear_txt, (0, 0))
        for i, p in enumerate(self.game.players.itervalues()):
            pygame.draw.rect(self.fear_surf, (255, 0, 0), pygame.Rect((self.fear_size[0], 32 * i), ((self.game.dimensions[0] - self.fear_size[0]) * (p.fear/float(MAX_FEAR)), 32)))
        self.game.screen_objects_to_draw.append((self.fear_surf, (0, self.game.dimensions[1] - nplayers * 32)))

    def draw_world_objects(self):  # stuff relative to camera
        for f in self.game.world_objects_to_draw:
            self.blit_camera(f)
        self.game.world_objects_to_draw = []

    def draw_screen_objects(self):  # stuff relative to screen
        for f in self.game.screen_objects_to_draw:
            f.draw()
        self.game.screen_objects_to_draw = []

    def blit_camera(self, sprite):
        # TODO: use built-in pyglet camera stuff
        old_x = sprite.x
        old_y = sprite.y
        sprite.set_position(old_x - self.game.camera_coords[0], old_y - self.game.camera_coords[1])
        sprite.draw()
        sprite.set_position(old_x, old_y)

    def draw_cutscene(self):
        #print game.cutscene_started
        #print hasattr(game, 'movie')
        #print game.GameState
    
        if self.game.cutscene_started and hasattr(self, 'movie'):
            if not self.movie.get_busy():
                self.game.GameState = MAIN_GAME
                self.game.cutscene_started = False
                self.game.clock.get_time()  # hack required for pygame.game.movie linux
                del self.movie  # hack required for pygame.movie mac os x
        else:
            self.surface.fill(black)
            pygame.display.update()
            try:
                f = BytesIO(open(self.game.cutscene_next, "rb").read())
                self.movie = pygame.movie.Movie(f)
                w, h = self.movie.get_size()
                self.movie.play()
                self.game.cutscene_started = True
            except IOError:
                print u"Video not found: " + self.game.cutscene_next
                self.game.set_state(MAIN_MENU)

    def draw_torch(self):
        ppos = (self.game.players['player1'].coord[0] + self.game.players['player1'].dimensions[0] / 2, self.game.players['player1'].coord[1] + self.game.players['player1'].dimensions[1] / 2)

        self.light_surf.fill((0, 0, 0, 0))
    
        hole = pygame.Rect((ppos[0] - self.light_size[0]/2 - self.game.camera_coords[0], ppos[1] - self.light_size[1]/2 - self.game.camera_coords[1]), self.light_size)

        self.clip_area = hole
    
        pygame.draw.rect(self.light_surf, (0, 0, 0, 255), pygame.Rect((0, 0), (self.game.dimensions[0], hole.top)))
        pygame.draw.rect(self.light_surf, (0, 0, 0, 255), pygame.Rect((0, 0), (hole.left, self.game.dimensions[1])))
        pygame.draw.rect(self.light_surf, (0, 0, 0, 255), pygame.Rect((hole.right, 0), (self.game.dimensions[0], self.game.dimensions[1])))
        pygame.draw.rect(self.light_surf, (0, 0, 0, 255), pygame.Rect((0, hole.bottom), (self.game.dimensions[0], self.game.dimensions[1])))
        self.light_surf.blit(self.light, (hole.left, hole.top))
        self.game.screen_objects_to_draw.append((self.light_surf, (0, 0)))

    def draw_text_box(self):
        self.surface.blit(self.game.text_box_test.background_surface,
                          (self.game.text_box_test.base_rect.x, self.game.text_box_test.base_rect.y),
                          self.game.text_box_test.draw_rect)
        self.surface.blit(self.game.text_box_test.text_surface,
                          (self.game.text_box_test.text_frame_rect.x + self.game.text_box_test.base_rect.x,
                           self.game.text_box_test.text_frame_rect.y + self.game.text_box_test.base_rect.y),
                          self.game.text_box_test.draw_rect)
