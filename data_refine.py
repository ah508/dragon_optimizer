import numpy as np
import os
import json

def fetch_dragon(dname):
    dragon = json.load(os.getcwd() + '/dragons/' + dname + '.json')
    return dragon

def fetch_template(tempname):
    template = json.load(os.getcwd() + '/lptemplates/' + tempname + '.json')
    template['constraints'] = np.asarray(template['constraints'])
    template['rhs'] = np.asarray(template['rhs'])
    return template

def find_template(lookupname):
    lookuptable = json.load(os.getcwd() + '/templatemap.json')
    key = next(k for k, v in lookuptable.items() if v == lookupname)
    return key

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
            return round(damage, 2)
    return dformula

def format_dragon(incoming):
    cur_dragon = fetch_dragon(incoming['dragon'])
    dformula = make_dformula(incoming['method'])
    if incoming['method'] == 'effmod':
        incoming['stats']['basestr'] = 1
    if incoming['method'] == 'puremod':
        incoming['dragon'] = incoming['dragon'] + 'NOBOOST'
    template = fetch_template(
        find_template(incoming['dragon'])
        )
    ...

    

    ##we need to know template formatting before we can proceed further
