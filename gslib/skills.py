import io
import json

from gslib.constants import *

class Skill(object):
    def __init__(self, name, prereqs, effects, cost, description):
        self.name = name
        self.prereqs = prereqs
        self.effects = effects
        self.cost = cost
        self.description = description

    def can_be_learnt(self, player):
        if self.name in player.skills_learnt:
            return False
        for skill in self.prereqs:
            if skill not in player.skills_learnt:
                return False
        return True


def load_skill_dict():
    with io.open(SKILLS_FILE, 'rt', encoding='utf-8') as f:
        raw_skill_dict = json.load(f)
    skill_dict = {}
    for key in raw_skill_dict:
        skill_dict[key] = Skill(key, raw_skill_dict[key]['prereqs'], raw_skill_dict[key]['effects'],
                                raw_skill_dict[key]['cost'], raw_skill_dict[key]['description'])
    return skill_dict
