__author__ = 'Michael'

import json
import os
from constants import *

class Skill(object):
    def __init__(self, name, prereqs, effect):
        self.name = name
        self.prereqs = prereqs
        self.effect = effect


def load_skill_dict():
    raw_skill_dict = json.load(open(SKILLS_FILE))
    skill_dict = {}
    for key in raw_skill_dict:
        skill_dict[key] = Skill(raw_skill_dict[key]['name'],raw_skill_dict[key]['prereqs'],raw_skill_dict[key]['effect'])
    return skill_dict





