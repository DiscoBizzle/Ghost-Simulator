import os
import json
from gslib import character_objects
from gslib import maps
from gslib import character_functions
from gslib import triggers
from gslib.constants import *

def create_save_char(charac):
    to_save = ['feared_function', 'possessed_function', 'unpossessed_function', 'harvested_function',
               'has_touched_function', 'is_touched_function', 'has_untouched_function', 'is_untouched_function',
               'stats', 'fears', 'scared_of', 'feared_speed', 'normal_speed',
               'states', 'coord', 'collision_weight']

    save_dict = {}
    for s in to_save:
        o = getattr(charac, s)
        if isinstance(o, list):
            if o:
                if hasattr(o[0], '__call__'): # check if function
                    t_list = [f.__name__ for f in o]
                    save_dict[s] = json.dumps(t_list)
                    continue

        save_dict[s] = json.dumps(o)

    save_dict[u'object_type'] = charac.__class__.__name__
    return save_dict


def create_save_trigger(trigger):
    save_dict = {}

    save_dict[u'object_references'] = trigger.object_references

    save_dict[u'trigger_type'] = trigger.__class__.__name__
    return save_dict


def save_map(m):
    print('Saving map: ' + m._name)
    obj_dict = {}
    for k, v in m.objects.iteritems():
        obj_dict[str(k)] = create_save_char(v)

    trig_dict = {}
    for k, v in m.triggers.iteritems():
        trig_dict[str(k)] = create_save_trigger(v)

    file_dict = {}
    file_dict[u'objects'] = obj_dict
    file_dict[u'triggers'] = trig_dict
    file_dict[u'name'] = m._name
    file_dict[u'tileset'] = m._tileset_file.replace('\\', '/')
    file_dict[u'map_file'] = m._map_file.replace('\\', '/')

    with open(os.path.join(SAVE_DIR, str(m._name + '_save.dat')), 'w') as f:
        json.dump(file_dict, f)
    f.close()


def create_save_state(m):
    obj_dict = {}
    for k, v in m.objects.iteritems():
        obj_dict[str(k)] = create_save_char(v)

    trig_dict = {}
    for k, v in m.triggers.iteritems():
        trig_dict[str(k)] = create_save_trigger(v)

    file_dict = {}
    file_dict[u'objects'] = obj_dict
    file_dict[u'triggers'] = trig_dict
    return file_dict


##########################################################################################################
character_type_map = {'Dude': character_objects.Dude,
                      'SmallDoor': character_objects.SmallDoor}

trigger_type_map = {'FlipStateOnHarvest': triggers.FlipStateOnHarvest,
                    'FlipStateWhenTouchedConditional': triggers.FlipStateWhenTouchedConditional,
                    'FlipStateWhenUnTouchedConditional': triggers.FlipStateWhenUnTouchedConditional}

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
            for f in func_list:
                if not 'trigger' in f:
                    function_type = afd[function_type_map[k]]
                    attr.append(function_type[f](new_obj))
        elif k != u'object_type':
            setattr(new_obj, k, json.loads(v))

    return new_obj


def load_trigger(m, d):
    obj_refs = d[u'object_references']
    new_trig = trigger_type_map[d[u'trigger_type']](m, *obj_refs)
    return new_trig

def load_map(game, map_name):
    with open(os.path.join(SAVE_DIR, str(map_name+ '_save.dat')), 'r') as f:
         map_dict = json.load(f)
    f.close()

    name = map_dict[u'name']
    tileset = map_dict[u'tileset']
    map_file = map_dict[u'map_file']
    new_map = maps.Map(name, tileset, map_file, game)

    for o_name, o_dict in map_dict[u'objects'].iteritems():
        new_map.objects[o_name] = load_object(game, o_dict)

    for t_name, t_dict in map_dict[u'triggers'].iteritems():
        new_map.triggers[t_name] = load_trigger(new_map, t_dict)

    return new_map


def restore_save_state(game, m, state_dict):
    for o_name, o_dict in state_dict[u'objects'].iteritems():
        m.objects[o_name] = load_object(game, o_dict)

    for t_name, t_dict in state_dict[u'triggers'].iteritems():
        m.triggers[t_name] = load_trigger(m, t_dict)