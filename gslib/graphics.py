import pygame
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO


# import Maps
from gslib.constants import *

# screen = pygame.display.set_mode((800, 800))
blue = pygame.Color(0, 255, 0)


def draw_map(m):
    grid_size = TILE_SIZE
    nw = len(m.grid)
    nh = len(m.grid[0])
    surf = pygame.Surface((nw * grid_size, nh * grid_size))

    for i in range(nw):
        for j in range(nh):
            area = m.grid[i][j].tileset_area
            surf.blit(m.tileset, (i * grid_size, j * grid_size), area)

            ##TEMPORARY - DRAWS SOLID TILES FOR COLLISION DEBUG
            #if not m.grid[i][j].walkable:
            #    temprect = pygame.Rect(i * grid_size, j * grid_size, TILE_SIZE, TILE_SIZE)
            #    pygame.draw.rect(surf, 0x0000ff, temprect)

    return surf

def draw_cutscene(game):
    #print game.cutscene_started
    #print hasattr(game, 'movie')
    #print game.GameState

    if game.cutscene_started and hasattr(game, 'movie'):
        if not game.movie.get_busy():
            game.GameState = MAIN_GAME
            game.cutscene_started = False
            game.clock.get_time()  # hack required for pygame.game.movie linux
            del game.movie  # hack required for pygame.movie mac os x
    else:
        game.surface.fill(pygame.Color(0, 0, 0))
        pygame.display.update()
        try:
            f = BytesIO(open(game.cutscene_next, "rb").read())
            game.movie = pygame.movie.Movie(f)
            w, h = game.movie.get_size()
            game.movie.play()
            game.cutscene_started = True
        except IOError:
            print "Video not found: " + game.cutscene_next
            game.GameState = MAIN_MENU
