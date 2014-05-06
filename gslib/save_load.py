import os
import json
from gslib import character_objects
from gslib import cutscene
from gslib import maps
from gslib import character_functions
from gslib import triggers
from gslib.constants import *


def save_cutscene_as_dict(cs):
    c_dict = {}
    for i in range(0, len(cs.actions)):
        c_dict[i] = cs.actions[i].save()
    return c_dict


def save_cutscenes(cutscenes, filename):
    cutscenes_dict = {}
    for cn, c in cutscenes.iteritems():
        cutscenes_dict[c.name] = save_cutscene_as_dict(c)

    with open(filename.replace('\\', '/'), 'w') as f:
        json.dump(cutscenes_dict, f)
    f.close()


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

    with open(os.path.join(SAVE_DIR, str(m._name + '_save.dat')), 'w') as f:
        json.dump(file_dict, f)
    f.close()


def create_save_state(m):
    obj_dict = {}
    for k, v in m.objects.iteritems():
        obj_dict[str(k)] = v.create_save_dict()#create_save_char(v)

    trig_dict = {}
    for k, v in m.triggers.iteritems():
        trig_dict[str(k)] = v.create_save_dict() #create_save_trigger(v)

    file_dict = {}
    file_dict[u'objects'] = obj_dict
    file_dict[u'triggers'] = trig_dict
    return file_dict


##########################################################################################################
character_type_map = {'Dude': character_objects.Dude,
                      'SmallDoor': character_objects.SmallDoor}

trigger_type_map = {'OnHarvest': triggers.OnHarvest,
                    'OnHarvestConditional': triggers.OnHarvestConditional,
                    'IsTouched': triggers.IsTouched,
                    'IsTouchedConditional': triggers.IsTouchedConditional}


function_type_map = {'has_touched_function': u'has_touched_functions',
                     'feared_function': u'when_scared_functions',
                     'possessed_function': u'become_possessed_functions',
                     'unpossessed_function': u'become_unpossessed_functions',
                     'harvested_function': u'when_harvested_functions',
                     'is_touched_function': u'is_touched_functions',
                     'has_untouched_function': u'has_untouched_functions',
                     'is_untouched_function': u'is_untouched_functions'}

def load_object(game, d):
    new_obj = character_type_map[d[u'object_type']](game)
    for k, v in d.iteritems():
        if '_function' in k:
            func_list = json.loads(v)
            afd = character_functions.all_functions_dict
            attr = getattr(new_obj, k)
            func_names = [a.__name__ for a in attr]
            for f in func_list:
                if not 'trigger' in f and not 'perf_actions' in f:
                    if not f in func_names:
                        function_type = afd[function_type_map[k]]
                        attr.append(function_type[f](new_obj))
        elif k != u'object_type':
            setattr(new_obj, k, json.loads(v))

    return new_obj


def load_trigger(game, d):
    obj_refs = d[u'object_references']
    actions = json.loads(d[u'actions'])

    actions_funcs = [triggers.trigger_functions_dict[a] for a in actions]
    new_trig = trigger_type_map[d[u'trigger_type']](game, *obj_refs, actions=actions_funcs)
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
    with open(cutscenes_file.replace('\\', '/'), 'r') as f:
        file_dict = json.load(f)
    f.close()

    cutscenes = {}
    for k, v in file_dict.iteritems():
        cutscenes[k] = load_cutscene_from_dict(game_, map_, k, v)

    return cutscenes


def load_map(game, map_name):
    with open(os.path.join(SAVE_DIR, str(map_name + '_save.dat')), 'r') as f:
        map_dict = json.load(f)
    f.close()

    name = map_dict[u'name']
    tileset = map_dict[u'tileset']
    map_file = map_dict[u'map_file']
    cutscenes_file = map_dict[u'cutscenes_file']
    new_map = maps.Map(name, tileset, map_file, cutscenes_file, game)

    for o_name, o_dict in map_dict[u'objects'].iteritems():
        new_map.objects[o_name] = load_object(game, o_dict)

    for t_name, t_dict in map_dict[u'triggers'].iteritems():
        new_map.triggers[t_name] = load_trigger(game, t_dict)

    new_map.cutscenes = load_cutscenes(game, new_map, cutscenes_file)

    return new_map


def restore_save_state(game, m, state_dict):
    m.objects = {}
    for o_name, o_dict in state_dict[u'objects'].iteritems():
        m.objects[o_name] = load_object(game, o_dict)

    m.triggers = {}
    for t_name, t_dict in state_dict[u'triggers'].iteritems():
        m.triggers[t_name] = load_trigger(m, t_dict)

    game.gather_buttons_and_drop_lists_and_objects()