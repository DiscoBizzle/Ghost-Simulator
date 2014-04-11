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

        self.possessing = None
        self.possess_range = POSSESSION_RANGE
        self.possess_key_up = True

        self.fear_collection_radius = FEAR_COLLECTION_RADIUS

        self.states = {'state1': {'max_speed': 5, 'fear_radius': 50},
                       'state2': {'max_speed': 10, 'fear_radius': 150}}
        self.normal_speed = 5

        self.collision_weight = 0


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
        # set current speed, then call parent update (handles movement and animation
        self.current_speed = self.normal_speed

        GameObject.update(self)

        # velocity is set by parent update function

        v_x, v_y = self.velocity

        if v_x != 0 or v_y != 0:
            self.fear -= FEAR_PER_STEP * (v_x * v_x + v_y * v_y) ** .5
        else:
            self.fear -= FEAR_PER_TICK

        if self.fear <= 0:
            self.game_class.GameState = GAME_OVER
            self.fear = START_FEAR

        if self.possessing:
            self.coord = self.possessing.coord
            self.velocity = (0, 0)

    def harvest_fear(self):  # AKA OOGA BOOGA
        for o in self.game_class.objects.itervalues():
            if not isinstance(o, Player):
                if self.check_distance(o, FEAR_COLLECTION_RADIUS):
                    # o.fear_collected()
                    self.fear += o.fear
                    for f in o.harvested_function:
                        f()
                        # o.harvested_function()

    def toggle_possess(self):
        if self.possessing:
            self.unpossess()
        else:
            self.possess_closest()

    def possess_closest(self):
        closest = (10000000000000, None)
        for o in self.game_class.objects.itervalues():
            if not isinstance(o, Player):
                # if o.possessed_by:
                #     continue
                if self.check_distance(o, self.possess_range):
                    d = self.get_distance_squared(o)
                    if d < closest[0]:
                        closest = (d, o)

        if closest[1]:
            self.possessing = closest[1]
            closest[1].possessed_by.append(self)
            for f in self.possessing.possessed_function:
                f()
            # self.possessing.possessed_function()
            # self.try_possess = False

    def unpossess(self):
        self.coord = self.possessing.coord
        for f in self.possessing.unpossessed_function:
            f()
        # self.possessing.unpossessed_function()
        self.possessing.possessed_by.remove(self)
        self.possessing = False

