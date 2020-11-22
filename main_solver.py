import numpy as np
from data_refine import dragon_template, format_constraints
from build_methods import make_getIndex
from lp_solver import get_lp_solution

'''infoset expected format, for future reference:

{
    dragon : 'dragon name'
    mode : one of 'effmod' 'puremod' or 'damage'
    transform time : total available transformation time
    skill :  boolean determining if skill should be used
    stats : {
        place all relevant damage stats here
        attack (base, passive, active, coab)
        skd (passive, active, coab)
        crit
        punisher
        break
        foe defense
        energy
        inspire
        bog
        aspd
        ahst
        bufftime
    }
    ... 

}

expected template name format:
    [special]
    or 
    [# of hits]hit[skill class]{boost}{dash}
    boost and dash are optional
    so, for agni it'd be
    "4hit1"
    for mars it'd be
    "5hit2boost"

'''

faux_infoset = {
    'dragon' : 'Agni',
    'mode' : 'puremod',
    'transform time' : 600,
    'skill' : True,
    'stats' : {
        'basestr' : 100,
        'passivestr' : .4,
        'activestr' : .4,
        'coabstr' :  .1,
        'passiveskd' : .4,
        'activeskd' : .1,
        'coabskd' : .15,
        'critchance' : .2,
        'critmod' : 0,
        'afflicpun' : 0,
        'breakmod' : 0,
        'breakpun' : 0,
        'basedef' : 10,
        'defmod' : 0,
        'aspd' : 0, 
        'ahst' : 0,
        'eleadv' : 1.5,
        'dboost' : 1.4,
        'energized' : False,
        'inspired' : False,
        'broken' : False,
        'bog' : False
    }
}

def get_transform_frames(minframe, dragon, statetree, time, getIndex):
    tframe = minframe
    for state in statetree:
        if state == 'size':
            continue
        for move in statetree[state]:
            i = getIndex(state, move)
            if dragon[move]['rtime'] != dragon[move]['dtime']:
                tframe -= time[i]
    return tframe

def solve(infoset):
    template, dragon = dragon_template(infoset['dragon'], infoset['mode'])
    # print(template['state tree'])
    getIndex = make_getIndex(template['state tree'])
    real_time, real_damage = format_constraints(template, dragon, infoset, getIndex)
    max_damage, min_frames, solution = get_lp_solution(template, real_time, real_damage)
    tframes = get_transform_frames(min_frames, dragon, template['state tree'], real_time, getIndex)

    print('SOLUTION:')
    print(f'max damage: {max_damage}')
    print(f'min frames: {min_frames}')
    print(f'transform frames: {tframes}')
    print(' ')
    print('SEQUENCE')
    print('--------')
    for k, v in solution.items():
        print(f'{k}       {v}')

solve(faux_infoset)
