import json

from gslib.constants import *


class Skill(object):
    def __init__(self, name, prereqs, effects):
        self.name = name
        self.prereqs = prereqs
        self.effects = effects

    def can_be_learnt(self, player):
        if self.name in player.skills_learnt:
            return False
        for skill in self.prereqs:
            if skill not in player.skills_learnt:
                return False
        return True


def load_skill_dict():
    raw_skill_dict = json.load(open(SKILLS_FILE))
    skill_dict = {}
    for key in raw_skill_dict:
        skill_dict[key] = Skill(key, raw_skill_dict[key]['prereqs'], raw_skill_dict[key]['effects'])
    return skill_dict




