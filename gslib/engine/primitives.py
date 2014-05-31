from __future__ import absolute_import, division, print_function

import pyglet
from pyglet.gl import *


class PrimitiveGroup(pyglet.graphics.Group):
    def __init__(self, blend_src, blend_dest, parent=None):
        super(PrimitiveGroup, self).__init__(parent)
        self.blend_src = blend_src
        self.blend_dest = blend_dest

    def set_state(self):
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)

    def unset_state(self):
        glPopAttrib()

    def __eq__(self, other):
        return (other.__class__ is self.__class__ and
                self.parent == other.parent and
                self.blend_src == other.blend_src and
                self.blend_dest == other.blend_dest)

    def __hash__(self):
        return hash((self.parent, self.blend_src, self.blend_dest))


class Primitive(object):

    # TODO: add move properties, similar to Sprite

    num_verts = None
    mode = None

    def __init__(self, x=0, y=0, color=(0, 0, 0, 255), blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA,
                 batch=None, group=None):
        self._x = x
        self._y = y

        self._color = color

        self._batch = batch
        self._group = PrimitiveGroup(blend_src, blend_dest, group)

        if self._batch is None:
            self._vertex_list = pyglet.graphics.vertex_list(self.num_verts, 'v2i', 'c4B')
        else:
            self._vertex_list = self._batch.add(self.num_verts, self.mode, self._group, 'v2i', 'c4B')

        self._update_colors()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        dx = x - self._x
        self._x = x
        self._move_x(dx)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        dy = y - self._y
        self._y = y
        self._move_y(dy)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self._update_colors()

    def draw(self):
        self._group.set_state_recursive()
        self._vertex_list.draw(self.mode)
        self._group.unset_state_recursive()

    def _update_colors(self):
        self._vertex_list.colors[:] = (self._color * self.num_verts)

    def _move_x(self, dx):
        self._vertex_list.vertices[::2] = map(lambda x: x + dx, self._vertex_list.vertices[::2])

    def _move_y(self, dy):
        self._vertex_list.vertices[1::2] = map(lambda y: y + dy, self._vertex_list.vertices[1::2])

    def _update_verticies(self):
        raise NotImplementedError()


class RectPrimitive(Primitive):

    num_verts = 4
    mode = GL_QUADS

    def __init__(self, x=0, y=0, width=0, height=0, rect=None, **kwargs):

        # passing in a Rect overrides x, y, width and height
        if rect is None:
            self._width = width
            self._height = height
        else:
            x, y = rect.bottomleft
            self._width = rect.width
            self._height = rect.height
        super(RectPrimitive, self).__init__(x=x, y=y, **kwargs)

        self._update_verticies()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width
        self._update_verticies()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height
        self._update_verticies()

    def _update_verticies(self):
        vertices = [
            self._x, self._y,
            self._x + self._width, self._y,
            self._x + self._width, self._y + self._height,
            self._x, self._y + self._height]
        self._vertex_list.vertices[:] = map(int, vertices)
