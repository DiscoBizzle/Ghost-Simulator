import pygame

WHITE = (255, 255, 255)
GREY = (60, 60, 60)


def test_info_draw(Character):
    screen = pygame.display.set_mode((800, 800))
    screen.blit(Character.info_sheet, (0, 0))
    pygame.display.update()
    raw_input()
    pygame.quit()


def fill_background(surface, border_size):
    border = pygame.image.load('info_sheet_border_tile.png')
    border = pygame.transform.scale(border, (border_size, border_size))
    bw = border.get_width()
    bh = border.get_height()
    w = surface.get_width()
    h = surface.get_height()

    for i in range(w/bw + 1):
        for j in range(h/bh + 1):
            surface.blit(border, (i*bw, j*bh))


def truncline(text, font, maxwidth):
        real = len(text)
        stext = text
        l = font.size(text)[0]
        cut = 0
        a = 0
        done = 1
        old = None
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


class Character(object):
    def __init__(self):
        self.stats = self.get_stats()
        self.info_sheet = self.draw_info_sheet()

    def get_stats(self):
        name = 'Bob'
        age = '18'
        image = 'sprite.png'
        bio = 'A colorless, lemon-lime flavored, caffeine-free soft drink, created by the Coca-Cola Company.'
        return {'name': name, 'age': age, 'image_name': image, 'bio': bio}

    def draw_info_sheet(self):
        font_size = 20
        dim = w, h = (400, 200)
        border = 8
        surf = pygame.Surface(dim)
        # surf.fill(GREY)
        fill_background(surf, border)

        # draw character image
        im = pygame.image.load(self.stats['image_name'])
        oldw = im.get_width()
        oldh = im.get_height()
        frac = (h - border*2) / float(oldh)
        neww = int(oldw * frac)
        im = pygame.transform.scale(im, (neww, h-border*2))
        surf.blit(im, (border, border))

        # draw name/age and text boxes
        font = pygame.font.SysFont('comic sans', font_size)
        name_text = font.render('Name: ' + self.stats['name'], 0, WHITE)
        age_text = font.render('Age: ' + self.stats['age'], 0, WHITE)

        text_left = neww + border*2

        temp = pygame.Surface((dim[0] - text_left - border, name_text.get_height() + age_text.get_height()))
        temp.fill(GREY)
        surf.blit(temp, (text_left, border))

        surf.blit(name_text, (text_left, border))
        surf.blit(age_text, (text_left, border + name_text.get_height()))

        temp = pygame.Surface((dim[0] - text_left - border, dim[1] - (name_text.get_height() + age_text.get_height() + 3*border)))
        temp.fill(GREY)
        surf.blit(temp, (text_left, name_text.get_height() + age_text.get_height() + 2*border))

        # draw bio
        bio = wrapline(self.stats['bio'], font, dim[0] - text_left - border)
        top = name_text.get_height() + age_text.get_height() + 2*border
        t_height = name_text.get_height()
        for i, b in enumerate(bio):
            t = font.render(b, 0, WHITE)
            surf.blit(t, (text_left, top + i * t_height))

        return surf


# pygame.init()
# pygame.font.init()
# test_info_draw(Character())