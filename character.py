import pygame

WHITE = (255, 255, 255)
GREY = (60, 60, 60)


def test():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800))
    char = Character('Sprite')
    screen.blit(char.info_sheet, (0, 0))
    screen.blit(char.sprite, (char.info_sheet.get_width() + 10, 0))
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


def load_stats(name):
    f = open('characters/' + name + '.txt')
    age = f.readline()
    age = age.strip()

    bio = ''
    fears = []
    start_bio = False
    for l in f:
        if l.strip() == '#':
            start_bio = True
        else:
            if start_bio:
                bio += l
            else:
                fears.append(l.strip())

    print fears
    return age, bio, fears


class Character(object):
    def __init__(self, name):
        self.fears = []
        self.stats = self.get_stats(name)
        self.info_sheet = self.draw_info_sheet()
        self.sprite = pygame.image.load('characters/' + name + '_top.png').convert()
        self.sprite.set_colorkey((255, 0, 255))

    def get_stats(self, name):
        name = name
        image = 'characters/' + name + '_front.png'
        age, bio, self.fears = load_stats(name)
        return {'name': name, 'age': age, 'image_name': image, 'bio': bio}

    def draw_info_sheet(self):
        font_size = 20
        dim = w, h = (400, 200)
        border = 8
        surf = pygame.Surface(dim)
        fill_background(surf, border)

        # draw character image
        im = pygame.image.load(self.stats['image_name']).convert()
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
        bio = text_wrap(self.stats['bio'], font, dim[0] - text_left - border)
        top = name_text.get_height() + age_text.get_height() + 2*border
        t_height = name_text.get_height()
        for i, b in enumerate(bio):
            t = font.render(b, 0, WHITE)
            surf.blit(t, (text_left, top + i * t_height))

        return surf

test()