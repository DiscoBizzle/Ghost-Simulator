from __future__ import absolute_import, division, print_function

import pyglet


class CameraGroup(pyglet.graphics.Group):
    def __init__(self, camera, parent=None):
        super(CameraGroup, self).__init__(parent=parent)
        self.camera = camera

    def set_state(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(-self.camera.x, -self.camera.y, 0)

    def unset_state(self):
        pyglet.gl.glPopMatrix()

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.parent == self.parent and
                other.camera is self.camera)

    def __hash__(self):
        return hash((self.parent, self.camera))


class Camera(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def undo_camera(self, position):
        x, y = position
        return x + self.x, y + self.y

    def apply_camera(self, position):
        x, y = position
        return x - self.x, y - self.y
