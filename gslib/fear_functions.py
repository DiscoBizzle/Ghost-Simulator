import pygame


def test():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    # surf = im_scared()
    surf = speech_bubble("LONGsdfalksdfjaslkfj alksjdf lkajdf lkajfdlkajsf lkasjdf lkajs flkaj", 200)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    raw_input()

def truncline(text, font, maxwidth):
    real = len(text)
    stext = text
    l = font.size(text)[0]
    cut = 0
    a = 0
    done = 1
    while l > maxwidth:
        a += 1
        n = text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext = n[:-cut]
        else:
            stext = n
        l = font.size(stext)[0]
        real = len(stext)
        done = 0
    return real, done, stext


def wrapline(text, font, maxwidth):
    done = 0
    wrapped = []

    while not done:
        nl, done, stext = truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text = text[nl:]
    return wrapped


def text_wrap(text, font, maxwidth):
    t = text.split('\n')
    wrapped = []
    for l in t:
        wrapped += wrapline(l, font, maxwidth)

    return wrapped


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
    pygame.draw.ellipse(surf, (200, 200, 200), pygame.Rect((5, 5), (size[0] - 10, size[1] - 10)))
    pygame.draw.polygon(surf, (60, 60, 60), ((0, surf.get_height()), (5, surf.get_height() * 2 / 3), (surf.get_width() * 1 / 3, surf.get_height() - 5)))

    for i, l in enumerate(lines):
        t = font.render(l, True, text_colour)
        surf.blit(t, (surf.get_width()/2 - t.get_width()/2, text_top + i * t.get_height()))

    surf.set_colorkey((255, 0, 255))
    return surf


def im_possessed(owner, game_class):
    def func():
        surf = speech_bubble("I'm possessed!", 150)
        pos = (owner.coord[0] + owner.dimensions[0], owner.coord[1] - surf.get_height())
        game_class.flair_to_draw.append((surf, pos))
    return func

