import pygame
import random

from gslib.game_object import GameObject
from gslib.constants import *

WHITE = (255, 255, 255)
GREY = (60, 60, 60)


def test():
    pygame.init()
    pygame.font.init()
    random.seed()
    screen = pygame.display.set_mode((800, 800))
    char = Character(None, 0, 0, 16, 32, gen_character({'image_name': 'characters/Sprite_front.png'}))
    screen.blit(char.info_sheet, (0, 0))
    screen.blit(char.sprite, (char.info_sheet.get_width() + 10, 0))
    pygame.display.update()
    print char.fears
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


def load_stats(fname):
    f = open('characters/' + fname)
    age = f.readline().strip()
    try:
        age = int(age)
    except ValueError:
        pass


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

def gen_character(stats=None):
    """Generate a character based on the stats dictionary.

    Any missing parameters in the dictionary are generated randomly.

      - age: integer
      - bio: string
      - fears: list of strings
      - name: string
      - gender: 'm' or 'f'
    """
    if stats is None:
        stats = {}
    stats.setdefault('age', random.randrange(151))
    stats.setdefault('bio', gen_bio())
    stats.setdefault('fears', gen_fears())
    stats.setdefault('feared_by', gen_fears())
    stats.setdefault('gender', random.choice(('m','f')))
    stats.setdefault('name', gen_name(stats['gender']))
    stats.setdefault('image_name', 'characters/Sprite_front.png')

    return stats

def choose_n_lines(n, fname):
    res = []
    with open(fname) as f:
        lines = f.readlines()
        for i in range(n):
            ix = random.randrange(len(lines))
            res.append(lines.pop(ix).strip())
    return res

def gen_bio():
    return ' '.join(choose_n_lines(3, "characters/bio.txt"))

def gen_fears():
    return choose_n_lines(random.randrange(1, 4), "characters/fear_description.txt")

def gen_name(gender):
    fname = "characters/first_names_{}.txt".format(gender)

    first_name = choose_n_lines(1, fname)[0]
    second_name = choose_n_lines(1, "characters/second_names.txt")[0]

    while random.random() > 0.9:
        second_name = "{}-{}".format(second_name, choose_n_lines(1, "characters/second_names.txt")[0])

    return "{} {}".format(first_name, second_name)


class Character(GameObject):
    def __init__(self, game_class, x, y, w, h, stats):

        GameObject.__init__(self, game_class, x, y, w, h, pygame.image.load('characters/DudeSheet.png').convert())
        self.fears = stats['fears']
        self.feared_by = stats['feared_by']
        self.feared_by.append('player')
        self.stats = stats
        self.info_sheet = self.draw_info_sheet()
        self.sprite = pygame.image.load('characters/Sprite_top.png')
        self.sprite = pygame.transform.scale(self.sprite, self.dimensions).convert()
        self.sprite.set_colorkey((255, 0, 255))

    def get_stats(self, name):
        name = name
        image = 'characters/' + name + '_front.png'
        age, bio, self.fears = load_stats(name)
        return {'name': name, 'age': age, 'image_name': image, 'bio': bio}

    def update(self):
        self.update_timer += 1
        if self.update_timer == 50:
            self.update_timer = 0
            mv = self.max_velocity
            self.velocity = (random.randint(-mv, mv), random.randint(-mv, mv))

        if self.fear_timer:
            fv = 10
            self.velocity = (random.randint(-fv, fv), random.randint(-fv, fv))
            self.fear_timer -= 1
        GameObject.update(self)

    def draw_info_sheet(self):
        font_size = 20
        dim = w, h = (GAME_WIDTH - LEVEL_WIDTH, LEVEL_HEIGHT)
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
        name_text = font.render('Name: ' + self.stats['name'], True, WHITE)
        age_text = font.render('Age: ' + str(self.stats['age']), True, WHITE)

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
            t = font.render(b, True, WHITE)
            surf.blit(t, (text_left, top + i * t_height))

        return surf



if __name__ == "__main__":
    test()