import numpy as np
import os
import json

def fetch_dragon(dname):
    dragon = json.load(os.getcwd() + '/dragons/' + dname + '.json')
    return dragon

def get_map(dragon):
    mapping = {}
    for k, v in dragon.items():
        if k == 'class':
            continue
        if v['mapnum']:
            mapping[v['mapnum']] = k
    return mapping

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
        def dformula(stats, base_mod, atype):
            return base_mod
    else:
        def dformula(stats, base_mod, atype):
            if stats['inspired'] and atype == 's':
                critc = 1
            else:
                critc = min(stats['critchance'], 1)
            if atype == 's':
                pskd = (stats['passiveskd'] + 0.5) if stats['energized'] else stats['passiveskd']
                skdcoeff = (1 + pskd)*(1 + stats['buffskd'])*(1 + stats['coabskd'])
            else:
                skdcoeff = 1
            if stats['broken']:
                breakcoeff = stats['breakmod']
                bpun = stats['brokepun']
            else:
                breakcoeff = 1
                bpun = 1
            critcoeff = critc*(1.7 + stats['critmod'])
            strcoeff = stats['basestr']*(1 + stats['passivestr'])*(1 + stats['activestr'])*(1 + stats['coabstr'])
            defcoeff = stats['basedef']*max((1-stats['defmod']), 0.5)*breakcoeff
            puncoeff = stats['afflicpun']*bpun
            damage = (5*strcoeff*base_mod*critcoeff*puncoeff*skdcoeff*stats['eleadv']*stats['dboost'])/(3*defcoeff)
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

def format_lp(template, dragon, infoset, getIndex):
    dformula = make_dformula(infoset['mode'])
    if infoset['mode'] == 'effmod':
        infoset['stats']['basestr'] = 1
    # basically, go on in and edit (as necessary):
    # presence of skill       [-1]
    # total frames            [-2]
    # buff frames             [-3]
    # buff frames 2           [-4]
    # buff frames 3 (overlap) [-5]
    # buff frames 4           [-6]
    # sp 1                    [-7]
    # sp 2                    [-8]
    # overlap 1               [-9]
    # overlap 2               [-10]
    # second skill selection  [-11]
    # usually it's just gonna be indices -1 through -3
    # make a way to figure out what doesn't exist
    # make the vector for the final damage constraint here too, 
    #   so you can just pass it to the actual solution method

    


    


