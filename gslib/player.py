import pygame

from gslib.constants import *
from gslib.game_object import GameObject

class Player(GameObject):
    def __init__(self, game_class, x, y, w, h, sprite_sheet_address):
        sprite_sheet = pygame.image.load(os.path.join(CHARACTER_DIR, sprite_sheet_address)).convert()
        GameObject.__init__(self, game_class, x, y, w, h, sprite_sheet)

        self.direction = DOWN
        self.animation_state = ANIM_DOWNIDLE
        self.frame_rect = pygame.Rect(self.current_frame * SPRITE_WIDTH, self.animation_state * SPRITE_HEIGHT,
                                      SPRITE_WIDTH, SPRITE_HEIGHT)

        self._fear = START_FEAR
        self.fears = ['player']
        self.skills_learnt = []

        self.possessing = False

        self.fear_collection_radius = FEAR_COLLECTION_RADIUS


    def get_fear(self):
        return self._fear

    def set_fear(self, f):
        self._fear = f
        if self._fear > MAX_FEAR:
            self._fear = MAX_FEAR

    fear = property(get_fear, set_fear)

    def learn_skill(self, skill):
        if self.game_class.skills_dict[skill].can_be_learnt(self):
            self.skills_learnt.append(self.game_class.skills_dict[skill].name)
            for effect in self.game_class.skills_dict[skill].effects:
                #apply effect
                pass
            return True
        return False

    def update(self):
        # update velocity
        v_x, v_y = 0, 0

        self.animation_state = self.direction

        if self.move_down:
            v_y += 10
            self.direction = DOWN
            self.animation_state = ANIM_DOWNWALK
        if self.move_up:
            v_y -= 10
            self.direction = UP
            self.animation_state = ANIM_UPWALK
        if self.move_left:
            v_x -= 10
            self.direction = LEFT
            self.animation_state = ANIM_LEFTWALK
        if self.move_right:
            v_x += 10
            self.direction = RIGHT
            self.animation_state = ANIM_RIGHTWALK

        self.frame_count += 1
        if (self.frame_count % 4) == 0:
            self.current_frame += 1

        if self.current_frame > self.max_frames:
            self.current_frame = 0

        self.frame_rect = pygame.Rect(self.current_frame * SPRITE_WIDTH, self.animation_state * SPRITE_HEIGHT,
                                      SPRITE_WIDTH, SPRITE_HEIGHT)

        self.velocity = (v_x, v_y)

        if v_x != 0 or v_y != 0:
            self.fear -= FEAR_PER_STEP * (v_x * v_x + v_y * v_y) ** .5
        else:
            self.fear -= FEAR_PER_TICK

        if self.fear <= 0:
            self.game_class.GameState = GAME_OVER
            self.fear = START_FEAR

        if self.possessing and self.game_class.toPossess:
            self.coord = self.game_class.toPossess.coord
            self.velocity = (0, 0)
        # move etc.
        GameObject.update(self)

        if self.game_class.toPossess and not self.possessing:
            if (self.coord[0] - self.game_class.toPossess.coord[0])**2 + (self.coord[1] - self.game_class.toPossess.coord[1])**2 < POSSESSION_RANGE**2:
                self.game_class.buttons['Possess'].enabled = True
                self.game_class.buttons['Possess'].colour = (120, 0, 0)
                self.game_class.buttons['Possess'].border_colour = (120, 50, 80)
            else:
                self.game_class.buttons['Possess'].enabled = False
                self.game_class.buttons['Possess'].colour = (60, 60, 60)
                self.game_class.buttons['Possess'].border_colour = (60, 25, 40)

