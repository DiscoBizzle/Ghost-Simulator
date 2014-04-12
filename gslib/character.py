import random
import os.path

import pygame

from gslib import fear_functions
from gslib.game_object import GameObject
from gslib import text_functions
from gslib.constants import *

WHITE = (255, 255, 255)
GREY = (60, 60, 60)

def test():
    pygame.init()
    pygame.font.init()
    random.seed()
    screen = pygame.display.set_mode((800, 800))
    char = Character(None, 0, 0, 16, 32, gen_character({'image_name': os.path.join(CHARACTER_DIR, 'Sprite_front.png')}))
    screen.blit(char.info_sheet, (0, 0))
    screen.blit(char.sprite, (char.info_sheet.get_width() + 10, 0))
    pygame.display.update()
    print char.fears
    raw_input()
    pygame.quit()


def fill_background(surface, border_size):
    border = pygame.image.load(os.path.join(TILES_DIR, 'info_sheet_border_tile.png'))
    border = pygame.transform.scale(border, (border_size, border_size))
    bw = border.get_width()
    bh = border.get_height()
    w = surface.get_width()
    h = surface.get_height()

    for i in range(w / bw + 1):
        for j in range(h / bh + 1):
            surface.blit(border, (i * bw, j * bh))


def load_stats(fname):
    f = open(os.path.join(CHARACTER_DIR, fname))
    age = f.readline().strip()
    age = int(age)

    bio = u''
    fears = []
    start_bio = False
    for l in f:
        if l.strip() == '#':
            start_bio = True
        else:
            if start_bio:
                bio += l.decode('utf-8')
            else:
                fears.append(l.strip().decode('utf-8'))

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
    stats.setdefault('scared_of', gen_fears())
    stats.setdefault('gender', random.choice(('m', 'f')))
    stats.setdefault('name', gen_name(stats['gender']))
    stats.setdefault('image_name', os.path.join(CHARACTER_DIR, 'Sprite_front.png'))

    return stats


def choose_n_lines(n, fname):
    res = []
    with open(fname) as f:
        lines = f.readlines()
        for i in range(n):
            ix = random.randrange(len(lines))
            res.append(lines.pop(ix).strip().decode('utf-8'))
    return res


def gen_bio():
    return u' '.join(choose_n_lines(3, os.path.join(CHARACTER_DIR, "bio.txt")))


def gen_fears():
    return choose_n_lines(random.randrange(1, 4), os.path.join(CHARACTER_DIR, "fear_description.txt"))


def gen_name(gender):
    fname = os.path.join(CHARACTER_DIR, "first_names_{}.txt".format(gender))

    first_name = choose_n_lines(1, fname)[0]
    second_name = choose_n_lines(1, os.path.join(CHARACTER_DIR, "second_names.txt"))[0]

    while random.random() > 0.9:
        second_name = u"{}-{}".format(second_name, choose_n_lines(1, os.path.join(CHARACTER_DIR, "second_names.txt"))[0])

    return u"{} {}".format(first_name, second_name)


class Character(GameObject):
    def __init__(self, game_class, x, y, w, h, stats, sprite_sheet='DudeSheet.png'):
        """
        Characters have various functions to determine their behaviour when things happen.
        self.feared_function - when the character is scared
        self.possessed_function - occurs when the character becomes possessed
        self.unpossessed_function - occurs when the character becomes unpossessed
        self.harvested_function - when the character has had its fear harvested (ooga booga'd)

        Make these functions in fear_functions.py
         - Function should take in any parameters and return a function.
         - Returned function should take 0 parameters.
        """
        GameObject.__init__(self, game_class, x, y, w, h, pygame.image.load(os.path.join(CHARACTER_DIR, sprite_sheet)).convert())
        if stats:
            self.fears = stats['fears']
            self.scared_of = stats['scared_of']
            self.scared_of.append('player')
        else:
            self.fears = []
            self.scared_of = []
        self.stats = stats
        self.info_sheet = self.draw_info_sheet()
        # self.sprite = pygame.image.load(os.path.join(CHARACTER_DIR, 'Sprite_top.png'))
        # self.sprite = pygame.transform.scale(self.sprite, self.dimensions).convert()
        # self.sprite.set_colorkey((255, 0, 255))
        self.feared_function = [fear_functions.freeze(self)]
        self.possessed_function = [fear_functions.im_possessed(self)]
        self.unpossessed_function = [fear_functions.undo_im_possessed(self)]
        self.harvested_function = [fear_functions.red_square(self)]
        self.fainted = False
        self.feared_by_obj = None
        self.feared_from_pos = (0, 0)

        self.possessed_by = []

    def get_stats(self, name):
        name = name
        image = os.path.join(CHARACTER_DIR, name) + '_front.png'
        age, bio, self.fears = load_stats(name)
        return {'name': name, 'age': age, 'image_name': image, 'bio': bio}

    def update(self):

        if not self.possessed_by:
            self.update_timer += 1
            #pick random direction (currently only one of 8 directions, but at a random speed)

            if self.update_timer >= 50 and not self.fear_timer:
                self.update_timer = 0
                self.current_speed = random.randint(self.min_speed, self.normal_speed)

                self.move_down = False
                self.move_up = False
                self.move_left = False
                self.move_right = False
                if random.randint(0, 1):
                    self.move_down = True
                else:
                    self.move_up = True

                if random.randint(0, 1):
                    self.move_right = True
                else:
                    self.move_left = True

            if self.fear_timer:
                for f in self.feared_function:
                    f()
                # self.feared_function()
                self.fear_timer -= 1

        else:
            # self.possessed_function(self)
            self.current_speed = self.normal_speed
            # tie move to possessing player move
            self.move_down = self.possessed_by[-1].move_down  # last player to possess get control
            self.move_up = self.possessed_by[-1].move_up
            self.move_left = self.possessed_by[-1].move_left
            self.move_right = self.possessed_by[-1].move_right

        GameObject.update(self)

    def draw_info_sheet(self):
        if not self.stats:
            return pygame.Surface((1, 1))
        font_size = 20
        #dim = w, h = (GAME_WIDTH - LEVEL_WIDTH, int((GAME_WIDTH - LEVEL_WIDTH) / 1.6))

        h = 200
        w = int(h * 1.6)
        dim = (w,h)

        border = 8
        surf = pygame.Surface(dim)
        fill_background(surf, border)

        # draw character image
        im = pygame.image.load(self.stats['image_name']).convert()
        oldw = im.get_width()
        oldh = im.get_height()
        frac = (h - border * 2) / float(oldh)
        neww = int(oldw * frac)
        im = pygame.transform.scale(im, (neww, h - border * 2))
        surf.blit(im, (border, border))

        # draw name/age and text boxes
        font = pygame.font.SysFont('comic sans', font_size)
        name_text = font.render(u'Name: ' + self.stats['name'], True, WHITE)
        age_text = font.render(u'Age: ' + str(self.stats['age']), True, WHITE)

        text_left = neww + border * 2

        temp = pygame.Surface((dim[0] - text_left - border, name_text.get_height() + age_text.get_height()))
        temp.fill(GREY)
        surf.blit(temp, (text_left, border))

        surf.blit(name_text, (text_left, border))
        surf.blit(age_text, (text_left, border + name_text.get_height()))

        temp = pygame.Surface(
            (dim[0] - text_left - border, dim[1] - (name_text.get_height() + age_text.get_height() + 3 * border)))
        temp.fill(GREY)
        surf.blit(temp, (text_left, name_text.get_height() + age_text.get_height() + 2 * border))

        # draw bio
        bio = text_functions.text_wrap(self.stats['bio'], font, dim[0] - text_left - border)
        top = name_text.get_height() + age_text.get_height() + 2 * border
        t_height = name_text.get_height()
        for i, b in enumerate(bio):
            t = font.render(b, True, WHITE)
            surf.blit(t, (text_left, top + i * t_height))

        return surf


if __name__ == "__main__":
    test()
