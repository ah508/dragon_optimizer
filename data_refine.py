import numpy as np
import math
import os
import json

def set_constraint(constraint, index, row, value):
    constraint[row, index] = value

def haste_sp(move, modifier):
    return math.ceil(move['sp']*(1 + modifier))

def fetch_dragon(dname):
    dragon = json.load(os.getcwd() + '/dragons/' + dname + '.json')
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
    if effect['type']:
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
        template = json.load(os.getcwd() + '/lptemplates/' + tempname + '.json')
    except FileNotFoundError:
        raise NotImplementedError(f'Template {tempname} not implemented')
    template['constraints'] = np.asarray(template['constraints'])
    template['rhs'] = np.asarray(template['rhs'])
    return template

def make_dformula(mode):
    if mode == 'puremod':
        def dformula(stats, base_mod):
            return base_mod
    else:
        def dformula(stats, move):
            base_mod = move['damage']
            atype = move['type']
            if stats['inspired'] and atype == 's':
                critc = 1
            else:
                critc = min(stats['critchance'], 1)
            if atype == 's':
                pskd = (stats['passiveskd'] + 0.5) if stats['energized'] else stats['passiveskd']
                skdcoeff = (
                    (1 + pskd)
                    *(1 + stats['buffskd'])
                    *(1 + stats['coabskd'])
                )
            else:
                skdcoeff = 1
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
    template['state tree'] = map_dict(template['state tree'], get_map(cur_dragon))
    return template, cur_dragon

def format_constraints(template, dragon, infoset, getIndex):
    dformula = make_dformula(infoset['mode'])
    real_time = np.zeros(template['state tree']['size'])
    real_damage = np.zeros(template['state tree']['size'])
    stats = infoset['stats']

    if infoset['mode'] == 'effmod':
        stats['basestr'] = 1
    for instruction in template['instructions']:
        if instruction['state'] == 'rhs':
            apply_rhs(
                instruction['input type'], 
                instruction['row'], 
                template['rhs'], 
                infoset
            )
            continue
        for move in template['state tree'][instruction['state']]:
            if move in instruction['omit']:
                continue
            index = getIndex(instruction['state'], move)
            damage = dformula(stats, dragon[move])
            frames = math.ceil(dragon[move]['dtime']/(1 + stats['aspd']))

            real_time[index] = math.ceil(dragon[move]['rtime']/(1 + stats['aspd']))
            real_damage[index] = damage
            if instruction['input type'] == 'frames':
                constr_val = frames
            elif instruction['input type'] == 'sp':
                constr_val = -1*haste_sp(dragon[move], stats['ahst'])
            elif instruction['input type'] == 'realframes':
                constr_val = real_time[index]
            
            set_constraint(
                template['constraints'], 
                index, instruction['row'], 
                constr_val
            )     
        apply_boost(stats, dragon[template['boost on']]['effect'])
    return real_time, real_damage