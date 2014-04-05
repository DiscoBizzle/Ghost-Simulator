import sys
import os
import pygame

if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:
    # On NT like Windows versions smpeg video needs windb.
    os.environ['SDL_VIDEODRIVER'] = 'windib'

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
    
pygame.init()
pygame.display.init()

f = BytesIO(open("movie.mpg", "rb").read())
movie = pygame.movie.Movie(f)
w, h = movie.get_size()

screen = pygame.display.set_mode((w, h))

movie.set_display(screen, pygame.Rect((5, 5), (w,h)))

movie.play()
