import time
import mip
from file_fetchers import fetch_dragon, fetch_key, load_data
from data_refine import generate_state_stats, get_model_variables
from build_methods import make_getIndex
from lp_solver import set_model_constraints, solve_model

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
    'dragon' : 'Corsaint Phoenix',
    'mode' : 'effmod',
    'transform time' : 600,
    'skill' : 1,
    'stats' : {
        'basestr' : 100,
        'passivestr' : 0,
        'activestr' : 0,
        'coabstr' :  0,
        'passiveskd' : 0,
        'activeskd' : 0,
        'coabskd' : 0,
        'critchance' : 0,
        'critmod' : 0,
        'afflicpun' : 0,
        'breakmod' : 0,
        'breakpun' : 0,
        'basedef' : 10,
        'defmod' : 0,
        'eleres' : 0,
        'aspd' : 0, 
        'ahst' : 0,
        'eleadv' : 1,
        'dboost' : 1,
        'energized' : False,
        'inspired' : False,
        'broken' : False,
        'bog' : False,
        'bufftime' : 0
    }
}

def solve(infoset, output=True):
    # startttime = time.time()
    model = mip.Model()
    drg = list(infoset['dragon'])
    for i in range(len(drg)):
        if drg[i] == ' ':
            drg[i] = '_'
    drg = ''.join(drg)
    # print(drg)
    # mtime = time.time() - startttime
    dragon = fetch_dragon(drg)
    temp_key = fetch_key(dragon['class'])
    template = load_data(temp_key, model)
    # fetchtime = time.time() - startttime
    getIndex = make_getIndex(template['state tree'])
    ref_vec = get_model_variables(model, template['state tree'], getIndex)
    state_values = generate_state_stats(template, dragon, infoset, getIndex)
    # settime = time.time() - startttime
    set_model_constraints(model, ref_vec, template, state_values, getIndex)
    solution = solve_model(model, ref_vec, state_values, output=output)
    return solution
    # solvetime = time.time() - startttime
    # print(mtime)
    # print(fetchtime)
    # print(settime)
    # print(solvetime)

solve(faux_infoset)
