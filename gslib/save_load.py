from __future__ import absolute_import, division, print_function

import io
import os
import json

from gslib import cutscene
from gslib import maps
from gslib.constants import *
from gslib.editor import trigger_edit
from gslib.game_objects import character, prop_objects


def save_cutscene_as_dict(cs):
    c_dict = {}
    for i in range(0, len(cs.actions)):
        c_dict[i] = cs.actions[i].save()
    return c_dict


def save_cutscenes(cutscenes, filename):
    cutscenes_dict = {}
    for cn, c in cutscenes.iteritems():
        cutscenes_dict[c.name] = save_cutscene_as_dict(c)

    with io.open(filename.replace('\\', '/'), 'wt', encoding='utf-8') as f:
        f.write(unicode(json.dumps(cutscenes_dict, ensure_ascii=False)))


def save_map(m):
    print('Saving map: ' + m._name)
    obj_dict = {}
    for k, v in m.objects.iteritems():
        obj_dict[str(k)] = v.create_save_dict()#create_save_char(v)

    trig_dict = {}
    for k, v in m.triggers.iteritems():
        trig_dict[str(k)] = v.create_save_dict()#create_save_trigger(v)

    save_cutscenes(m.cutscenes, m._cutscenes_file)

    file_dict = {}
    file_dict[u'objects'] = obj_dict
    file_dict[u'triggers'] = trig_dict
    file_dict[u'name'] = m._name
    file_dict[u'tileset'] = m._tileset_file.replace('\\', '/')
    file_dict[u'map_file'] = m._map_file.replace('\\', '/')
    file_dict[u'cutscenes_file'] = m._cutscenes_file.replace('\\', '/')

    with io.open(os.path.join(MAPS_DIR, str(m._name + '_data.json')), 'wt', encoding='utf-8') as f:
        f.write(unicode(json.dumps(file_dict, ensure_ascii=False)))


def create_save_state(m):
    obj_dict = {}
    for k, v in m.objects.iteritems():
        obj_dict[str(k)] = v.create_save_dict()

    trig_dict = {}
    for k, v in m.triggers.iteritems():
        trig_dict[str(k)] = v.create_save_dict()

    file_dict = {}
    file_dict[u'objects'] = obj_dict
    file_dict[u'triggers'] = trig_dict
    return file_dict


##########################################################################################################
# character_type_map = {'Dude': character_objects.Dude,
#                       'SmallDoor': character_objects.SmallDoor,
#                       'Bomb': character_objects.Bomb,
#                       'SpriteBoss': character_objects.SpriteBoss}


def load_object(game, d):
    name = d[u'object_type']
    if '_prop' in name:
        new_obj = prop_objects.possible_props[name[:-5]](game)
    else:
        new_obj = character.Character(game, 0, 0, 32, 32)
    new_obj.load_from_dict(d)

    return new_obj


def load_trigger(game, d):
    new_trig = trigger_edit.Trigger(game)
    new_trig.load_from_dict(d)
    return new_trig


def load_cutscene_from_dict(game_, map_, name, d):
    actions = []
    if d.keys():
        for k in range(min(map(int, d.keys())), max(map(int, d.keys())) + 1):
            act_d = d[unicode(k)]
            cl = getattr(cutscene, act_d['class_name'])
            actions.append(cl(game_, map_, act_d))
    return cutscene.Cutscene(name, actions)


def load_cutscenes(game_, map_, cutscenes_file):
    with io.open(cutscenes_file.replace('\\', '/'), 'rt', encoding='utf-8') as f:
        file_dict = json.load(f)

    cutscenes = {}
    for k, v in file_dict.iteritems():
        cutscenes[k] = load_cutscene_from_dict(game_, map_, k, v)

    return cutscenes


def load_map(game, map_name):
    with io.open(os.path.join(MAPS_DIR, str(map_name + '_data.json')), 'rt', encoding='utf-8') as f:
        map_dict = json.load(f)

    name = map_dict[u'name']
    tileset = map_dict[u'tileset']
    map_file = map_dict[u'map_file']
    cutscenes_file = map_dict[u'cutscenes_file']
    new_map = maps.Map(name, tileset, map_file, cutscenes_file, game)

    prev_map = None
    if not game.map is None:
        prev_map = game.map
    game.map = new_map

    new_map.reset_fears_dict()
    prop_list = []
    for o_name, o_dict in map_dict[u'objects'].iteritems():
        if '_prop' in o_name:
            prop_list.append((o_name, o_dict))
        else:
            new_map.objects[o_name] = load_object(game, o_dict)

    for o_name, o_dict in prop_list: # have to load props second so they can be "held by" objects that already exist
        new_map.objects[o_name[:-5]] = load_object(game, o_dict)

    for t_name, t_dict in map_dict[u'triggers'].iteritems():
        new_map.triggers[t_name] = load_trigger(game, t_dict)

    new_map.cutscenes = load_cutscenes(game, new_map, cutscenes_file)

    if not prev_map is None:
        game.map = prev_map
    return new_map


def restore_save_state(game, m, state_dict):
    m.triggers.clear() # empties the dict, but preserves its place in memory (prevents breaking references to it)
    m.objects.clear() # empties the dict, but preserves its place in memory (prevents breaking references to it)
    m.reset_fears_dict()

    for o_name, o_dict in state_dict[u'objects'].iteritems():
        m.objects[o_name] = load_object(game, o_dict)

    game.gather_buttons_and_drop_lists_and_objects()

    for t_name, t_dict in state_dict[u'triggers'].iteritems():
        m.triggers[t_name] = load_trigger(game, t_dict)

    # game.gather_buttons_and_drop_lists_and_objects()
