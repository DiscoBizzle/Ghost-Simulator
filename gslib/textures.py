import pyglet.image

_loaded = {}

def get(filename):
    fid = filename.lower()

    if not fid in _loaded:
        _loaded[fid] = pyglet.image.load(filename).get_texture()

    return _loaded[fid]
