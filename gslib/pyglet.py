
# this file gets pyglet into the modules table one way or another

import sys

if not hasattr(sys, 'already_pyglet'):

  if hasattr(sys, 'pyglet_stench'):
    raise ImportError('failed to find the real pyglet')

  sys.path.insert(0, '../Ghost-Simulator/deps/pyglet-9781eb46dca2')
  sys.path.insert(1, '../deps/pyglet-9781eb46dca2')

  sys.pyglet_stench = True

  try:
    import pyglet
  except:
    pass

  if __name__ == 'pyglet':
    reload(pyglet)
  
  sys.already_pyglet = True

