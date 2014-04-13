import pyglet.text

from gslib.constants import *

# TODO: if text rendering is too slow, make a func that uses pyglet.font.* instead.
# pyglet.text looks like it's the slower but more complete option.

def new(font=FONT, font_size=36, text='no text', centered=False, width=None, height=None):
    wrapped = (width is not None)
    return pyglet.text.Label(text, font, font_size, width=width, height=height,
              anchor_x='left', anchor_y='bottom', align=('center' if centered else 'left'),
              multiline=wrapped)

def speech_bubble(text, width, text_colour=(0, 0, 0)):
    font = pygame.font.SysFont('helvetica', 14)

    text_left = 20
    text_top = 20
    lines = text_wrap(text, font, width-text_left*2)
    t = font.render(lines[0], True, text_colour)
    size = (width, 2*text_top + len(lines) * t.get_height())

    surf = pygame.Surface(size)
    surf.fill((255, 0, 255))
    pygame.draw.ellipse(surf, (60, 60, 60), pygame.Rect((0, 0), size))
    pygame.draw.polygon(surf, (60, 60, 60), ((0, surf.get_height()), (5, surf.get_height() * 2 / 3), (surf.get_width() * 1 / 3, surf.get_height() - 5)))
    pygame.draw.ellipse(surf, (200, 200, 200), pygame.Rect((5, 5), (size[0] - 10, size[1] - 10)))


    for i, l in enumerate(lines):
        t = font.render(l, True, text_colour)
        surf.blit(t, (surf.get_width()/2 - t.get_width()/2, text_top + i * t.get_height()))

    surf.set_colorkey((255, 0, 255))
    return surf
