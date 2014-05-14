try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

import os.path

import pyglet.image

from gslib.constants import *
from gslib import player
from gslib import sprite
from gslib import textures
from gslib import text
from gslib import primitives


circle_tex = None
def draw_circle(r, color):
    global circle_tex
    if circle_tex is None:
        circle_tex = textures.get(os.path.join(CHARACTER_DIR, 'circle_solid.png'))
    sprit = sprite.Sprite(circle_tex)
    sprit.scale_x = 2*r / 1024.0
    sprit.scale_y = 2*r / 1024.0
    sprit.color_rgba = color + (120,)
    return sprit


class Graphics(object):
    """
    see Game class for how to add things to be drawn.
    """
    def __init__(self, game):
        self.game = game
        #self.surface = pygame.display.set_mode(self.game.dimensions, pygame.RESIZABLE)

        self.field = sprite.Sprite(pyglet.image.load(os.path.join(TILES_DIR, 'field.png')).get_texture())
        self.field.opacity = self.game.options['VOF_opacity']
        #self.field.scale_x = self.game.dimensions[0] / self.field.image.width
        #self.field.scale_y = self.game.dimensions[1] / self.field.image.height

        self.light = sprite.Sprite(pyglet.image.load(os.path.join(TILES_DIR, 'light.png')).get_texture())
        self.light.scale_x = self.light.scale_y = (200.0 / self.light.image.height)
        self.light_size = (self.light.width, self.light.height)

        #font = pygame.font.SysFont(FONT, 20)
        #self.fear_size = font.size(u"FEAR")
        #self.fear_txt = font.render(u"FEAR", True, (200, 200, 200)).convert_alpha()
        #self.fear_surf = pygame.Surface((self.game.dimensions[0], 32)).convert_alpha()
        self.fear_text = text.new(FONT, 20, u'FEAR')

        self.game_over_txt1 = pyglet.text.Label(u"GAME OVER", FONT, 80, color=(255, 255, 255, 255),
                                                anchor_x='left', anchor_y='bottom', align='center')

        self.game_over_txt2 = pyglet.text.Label(u"press esc scrub", FONT, 20, color=(255, 255, 255, 255),
                                                anchor_x='left', anchor_y='bottom', align='center')

        self.last_map = None
        self.map_texture = {}
        self.tile_sprite = {}

        self.game.options.push_handlers(self)

    def on_option_change(self, key, old_value, value):
        if key == 'VOF_opacity':
            self.field.opacity = value

    def draw_game_over(self):
        self.game_over_txt1.x = (self.game.dimensions[0] - self.game_over_txt1.content_width) / 2
        self.game_over_txt1.y = (self.game.dimensions[1] - self.game_over_txt1.content_height) / 2
        self.game.screen_objects_to_draw.append(self.game_over_txt1)

        self.game_over_txt2.x = (self.game.dimensions[0] - self.game_over_txt2.content_width) / 2
        self.game_over_txt2.y = (self.game.dimensions[1] - self.game_over_txt2.content_height -
                                 self.game_over_txt1.content_height) / 2
        self.game.screen_objects_to_draw.append(self.game_over_txt2)

    def main_game_draw(self):
        # this runs faster than game update. animation can be done here with no problems.
        if self.game.state != MOVIE:
            self.game.window.clear()

        if self.game.state == STARTUP:
            pass
        elif self.game.state == MAIN_MENU:
            self.game.main_menu.draw()
        elif self.game.state == MAIN_GAME or self.game.state == EDITOR:
            self.draw_map_early()
            self.draw_objects()
            self.draw_map_late()
            if self.game.options['torch']:
                self.draw_torch()

            self.draw_buttons()
            self.draw_drop_lists()
            if self.game.state == EDITOR:
                self.draw_editor()

            self.draw_fear_bar()
            self.draw_character_stats()

            if self.game.show_fears:
                self.game.say_fears()
            if self.game.show_ranges:
                self.game.show_fear_ranges()

            if self.game.text_box is not None:
                self.game.text_box.draw()

            if self.game.message_box is not None:
                self.game.message_box.draw()

        elif self.game.state == GAME_OVER:
            self.draw_game_over()
        elif self.game.state == CREDITS:
            self.game.credits.draw()
        elif self.game.state == SKILLS_SCREEN:
            self.game.skill_menu.draw()
        elif self.game.state == OPTIONS_MENU:
            self.game.options_menu.draw()
        elif self.game.state == KEYBIND_MENU or self.game.state == KEYBIND_CAPTURE:
            self.game.keybind_menu.draw()
        elif self.game.state == MOVIE:
            self.game.movie_player.draw()

        if self.game.options['FOV']:
            self.draw_world_objects()
            self.draw_screen_objects()

        if self.game.options['VOF']:
            self.field.draw()

    def _draw_map(self):
        m = self.game.map

        if self.last_map != m:
            #print('Redrawing map...')
            #start_time = time.clock()

            grid_size = TILE_SIZE

            self.map_texture = {}
            self.tile_sprite = {}

            for layer_name, layer in m.grid.iteritems():
                self.map_texture[layer_name] = pyglet.image.Texture.create(grid_size * m.grid_width, grid_size * m.grid_height)
                self.tile_sprite[layer_name] = sprite.Sprite(self.map_texture[layer_name])

            for layer_name, layer_texture in self.map_texture.iteritems():
                for y in range(m.grid_height):
                    for x in range(m.grid_width):
                        layer_texture.blit_into(m.tileset_seq[m.grid[layer_name][y][x].tileset_coord], x * grid_size, y * grid_size, 0)

            self.last_map = m

            #print('Map redraw complete (took ' + str(time.clock() - start_time) + 's)')

    def draw_map_early(self):
        self._draw_map()

        for layer_name, layer_sprite in self.tile_sprite.iteritems():
            if layer_name.startswith("ground"):
                self.game.world_objects_to_draw.insert(0, layer_sprite)

    def draw_map_late(self):
        for layer_name, layer_sprite in self.tile_sprite.iteritems():
            if layer_name.startswith("sky"):
                self.game.world_objects_to_draw.append(layer_sprite)

    def draw_editor(self):
        trig = self.game.editor.trigger_editor.drop_lists['triggers'].selected
        if not trig is None:
            zone = self.game.editor.trigger_editor.drop_lists['zones'].selected
            for z in trig.zones:
                r = primitives.RectPrimitive(rect=z, color=(135, 206, 250), opacity=50)
                if not zone is None:
                    if z == zone:
                        r = primitives.RectPrimitive(rect=z, color=(65, 105, 225), opacity=100)

                self.game.world_objects_to_draw.append(r)


    def draw_buttons(self):
        for button in dict(self.game.buttons, **self.game.editor.get_buttons() if self.game.state == EDITOR else {}).itervalues():
            if not button.visible:
                continue
            self.game.screen_objects_to_draw.append(button)

    def draw_drop_lists(self):
        priority_buttons = []
        for l in dict(self.game.drop_lists, **self.game.editor.get_lists() if self.game.state == EDITOR else {}).itervalues():
            if not l.visible:
                continue
            if hasattr(l, 'main_button'):
                self.game.screen_objects_to_draw.append(l.main_button)
            if not l.open:
                continue
            for b in l.drop_buttons:
                if l.open and l.__class__.__name__ != "List":
                    priority_buttons.append(b)
                else:
                    self.game.screen_objects_to_draw.append(b)

            if hasattr(l, 'slider'):
                if l.open:
                    priority_buttons.append(l.slider)
                else:
                    self.game.screen_objects_to_draw.append(l.slider)
        self.game.screen_objects_to_draw += priority_buttons

    def draw_objects(self):
        for o in sorted(self.game.objects.values() + self.game.map.static_objects, key=(lambda obj: -obj.coord[1])):
            if isinstance(o, player.Player):
                if o.possessing:
                    continue

            x = o.coord[0]
            y = o.coord[1]
            object_sprite = o.sprite
            self.game.world_objects_to_draw.append(object_sprite)

            for s, p in o.flair.itervalues():
                s.set_position(x + p[0] + object_sprite.width / 2, y + p[1] + object_sprite.height / 2)
                self.game.world_objects_to_draw.append(s)

            if o == self.game.selected_object:
                r = o.highlight_radius
                sprit = draw_circle(r, (200, 0, 0))
                sprit.x = o.coord[0] + o.sprite_width/2 - r
                sprit.y = o.coord[1] + o.sprite_height/2 - r
                self.game.world_objects_to_draw.append(sprit)

    def draw_character_stats(self):
        if self.game.disp_object_stats:
            border = 4
            o = self.game.object_stats  # background, image, name, age
            o[1].x = self.game.dimensions[0] - o[1].width - o[2].content_width - border
            o[1].y = self.game.dimensions[1] - o[1].height - border
            o[0].x, o[0].y = o[1].x - border, o[1].y - border
            o[2].x = o[1].x + o[1].width
            o[2].y = self.game.dimensions[1] - o[2].content_height
            o[3].x = o[2].x
            o[3].y = o[2].y - o[2].content_height
            self.game.screen_objects_to_draw += o  # self.game.object_stats

    def draw_fear_bar(self):
        nplayers = len(self.game.players)
        self.game.screen_objects_to_draw.append(self.fear_text)
        w = self.game.dimensions[0] - self.fear_text.content_width
        h = 32
        for i, p in enumerate(self.game.players.itervalues()):
            sp = primitives.RectPrimitive(x=self.fear_text.content_width,
                                          y=h * i,
                                          width=w * (p.fear / float(MAX_FEAR)),
                                          height=h,
                                          color=(255, 0, 0))
            self.game.screen_objects_to_draw.append(sp)

    def draw_world_objects(self):  # stuff relative to camera
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(-self.game.camera_coords[0], -self.game.camera_coords[1], 0)
        for f in self.game.world_objects_to_draw:
            f.draw()
        pyglet.gl.glPopMatrix()
        self.game.world_objects_to_draw = []

    def draw_screen_objects(self):  # stuff relative to screen
        for f in self.game.screen_objects_to_draw:
            if f is None:
                print(self.game.screen_objects_to_draw)
            f.draw()
        self.game.screen_objects_to_draw = []

    def draw_torch(self):
        raise Exception("graphics.draw_torch() not ported to pyglet.")

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

