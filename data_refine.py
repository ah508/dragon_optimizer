import numpy as np
import math
import os
import json

def set_constraint(constraint, index, row, value):
    constraint[row, index] = value

def haste_sp(move, modifier):
    return math.ceil(move['sp']*(1 + modifier))

def find_speed(move, base, modifier):
    if move in ['T', 'D', 'BD']:
        return base
    return math.ceil(base/(1 + modifier))

def get_duration(dragon, move, speed):
    bstart = find_speed(move, dragon[move]['effect']['timing'], speed)
    skend = find_speed(move, dragon[move]['rtime'], speed)
    return dragon[move]['effect']['duration'] - skend + bstart

def fetch_dragon(dname):
    with open(os.getcwd() + '/dragons/' + dname + '.json') as f:
        dragon = json.loads(f.read())
    return dragon

def apply_rhs(input_type, row, rhs, infoset):
    if input_type == 'skill':
        rhs[row] = 1 if infoset['skill'] else 0
    else:
        rhs[row] = infoset[input_type]

def get_map(dragon):
    mapping = {}
    for k, v in dragon.items():
        if k == 'class':
            continue
        if v['mapnum']:
            mapping[v['mapnum']] = k
    return mapping

def apply_boost(stats, effect):
    if isinstance(effect['type'], list):
        for i in range(len(effect['type'])):
            if effect['type'][i] == 'bog':
                stats[effect['type']] = True
            else:
                stats[effect['type']] += effect['value'][i]
    elif effect['type']:
        if effect['type'] == 'bog':
            stats[effect['type']] = True
        else:
            stats[effect['type']] += effect['value']

def map_dict(old_dict, mapping):
    '''Provides re-keying for specific nested keys in a dict.

    Maps a dictionary to a different dictionary with identical values,
    but differing keys. If a mapping is not provided, defaults to the
    original key-value pair. Right now this is exclusively for the
    second set of keys in a nested dictionary with a known format, but
    may be generalized at a later date.

    Parameters
    ----------
    old_dict : { }
        The dictionary to be re-keyed.
    mapping: { }
        A dictionary mapping from old to new keys.
    
    Returns
    -------
    new_dict: { }
        A dictionary identical to old_dict, but with different key names.
    '''

    new_dict = {}
    for k, v in old_dict.items():
        if k == 'size':
            new_dict[k] = v
            continue
        new_dict[k] = {}
        for k2, v2 in v.items():
            try:
                new_dict[k][mapping[k2]] = v2
            except KeyError:
                new_dict[k][k2] = v2
    return new_dict

def fetch_template(dragclass, boost):
    if dragclass['forbidden']:
        raise NotImplementedError('Dragon not implemented')
    if dragclass['special']:
        tempname = dragclass['special']
    else:
        tempname = dragclass['hit'] + 'hit' + dragclass['skill']
        if dragclass['buff'] and boost:
            tempname = tempname + 'boost'
        if dragclass['dash']:
            tempname = tempname + dragclass['dash']
    try:
        with open(os.getcwd() + '/lptemplates/' + tempname + '.json') as f:
            template = json.loads(f.read())
    except FileNotFoundError:
        raise NotImplementedError(f'Template {tempname} not implemented')
    template['constraints'] = np.asarray(template['constraints'])
    template['rhs'] = np.asarray(template['rhs'])
    return template

def make_dformula(mode):
    if mode == 'puremod':
        def dformula(stats, base_mod, atype):
            return base_mod
    else:
        def dformula(stats, base_mod, atype, energized=True, inspired=True):
            if stats['inspired'] and atype == 's' and inspired:
                critc = 1
            else:
                critc = min(stats['critchance'], 1)
            if atype == 's':
                if stats['energized'] and energized:
                    pskd = stats['passiveskd'] + 0.5
                else:
                    pskd = stats['passiveskd']
                skdcoeff = (
                    (1 + pskd)
                    *(1 + stats['buffskd'])
                    *(1 + stats['coabskd'])
                )
            else:
                skdcoeff = 1
            # if atype == 'f':
            #     fscoeff = (
            #         (1 + stats['passivefs'])
            #         *(1 + stats['activefs'])
            #         *(1 + stats['coabfs'])
            #     )
            # else:
            #     fscoeff = 1
            if stats['broken']:
                breakcoeff = stats['breakmod']
                bpun = stats['brokepun']
            else:
                breakcoeff = 1
                bpun = 1
            critcoeff = critc*(1.7 + stats['critmod'])
            puncoeff = stats['afflicpun']*bpun
            strcoeff = (
                stats['basestr']
                *(1 + stats['passivestr'])
                *(1 + stats['activestr'])
                *(1 + stats['coabstr'])
            )
            defcoeff = (
                stats['basedef']
                *max((1-stats['defmod']), 0.5)
                *breakcoeff
            )
            damage = (
                (5/3)
                *strcoeff
                *base_mod
                *critcoeff
                *puncoeff
                *skdcoeff
                # *fscoeff
                *stats['eleadv']
                *stats['dboost']
                /defcoeff
            )
            if stats['bog']:
                damage *= 1.5
            return round(damage, 2)
    return dformula

def dragon_template(dragon, mode):
    cur_dragon = fetch_dragon(dragon)
    boost = False if mode == 'puremod' else True
    template = fetch_template(cur_dragon['class'], boost)
    template['state tree'] = map_dict(template['state tree'], 
                                      get_map(cur_dragon))
    return template, cur_dragon

def format_constraints(template, dragon, infoset, getIndex):
    dformula = make_dformula(infoset['mode'])
    real_time = np.zeros(template['state tree']['size'])
    real_damage = np.zeros(template['state tree']['size'])
    stats = infoset['stats']
    real_damage[0] = dformula(stats, dragon['T']['ndamage'], dragon['T']['type'])
    if template['boost on']:
        infoset['buff duration'] = get_duration(dragon, 
                                                template['boost on'], 
                                                stats['aspd'])
    # NOTE: if the buff is attack speed, this results in inaccurate handling
    # this can be fixed with relative easy, for whoever next works on this
    
    if infoset['mode'] == 'effmod':
        stats['basestr'] = 1
    for instruction in template['instructions']:
        if instruction['state'] == 'rhs':
            apply_rhs(
                instruction['input type'], 
                instruction['row'], 
                template['rhs'], 
                infoset)
            continue

        hold = []
        for move in template['state tree'][instruction['state']]:
            if move in instruction['omissions']:
                continue
            index = getIndex(instruction['state'], move)
            frames = find_speed(
                move, 
                dragon[move]['dtime'], 
                stats['aspd'])

            real_damage[index] = dformula(
                stats, 
                dragon[move]['ndamage'], 
                dragon[move]['type'])
            if dragon[move]['bdamage'] and move != template['boost on']:
                real_damage[index] += dformula(stats, 
                                               dragon[move]['bdamage'], 
                                               dragon[move]['type'])
            elif dragon[move]['bdamage'] and move == template['boost on']:
                hold.append(index)
                hold.append(dragon[move]['bdamage'])
                hold.append(dragon[move]['type'])

            real_time[index] = find_speed(move, 
                                          dragon[move]['rtime'], 
                                          stats['aspd'])
            if instruction['input type'] == 'frames':
                constr_val = frames
            elif instruction['input type'] == 'sp':
                constr_val = -1*haste_sp(dragon[move], stats['ahst'])
            elif instruction['input type'] == 'realframes':
                constr_val = real_time[index]
            
            set_constraint(
                template['constraints'], 
                index, instruction['row'], 
                constr_val)
        if template['boost on']:
            apply_boost(stats, dragon[template['boost on']]['effect'])
            if hold:
                real_damage[hold[0]] += dformula(stats, hold[1], hold[2])
    return real_time, real_damage