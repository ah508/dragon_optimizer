import time
import mip
from file_fetchers import fetch_dragon, fetch_key, load_data
from data_refine import generate_state_stats, get_model_variables
from build_methods import make_getIndex
from lp_solver import set_model_constraints, solve_model

def solve(infoset, output=True):
    startttime = time.time()
    model = mip.Model()
    drg = list(infoset['dragon'])
    for i in range(len(drg)):
        try:
            drg[i] = drg[i].encode('latin1').decode('unicode_escape')
        except UnicodeEncodeError:
            pass
        if drg[i] == ' ':
            drg[i] = '_'
    drg = ''.join(drg)
    dragon = fetch_dragon(drg)
    temp_key = fetch_key(dragon['class'])
    template = load_data(temp_key, model)
    getIndex = make_getIndex(template['state tree'])
    ref_vec = get_model_variables(model, template['state tree'], getIndex)
    state_values = generate_state_stats(template, dragon, infoset, getIndex)
    set_model_constraints(model, ref_vec, template, state_values, getIndex)
    solution = solve_model(model, ref_vec, state_values, output=output, relaxation=infoset['relax'])
    solvetime = time.time() - startttime
    solution['solvetime'] = solvetime
    return solution

def check_input(input_dict):
    errlist = []
    if 'dragon' not in input_dict:
        errlist.append('"dragon" is a mandatory field')
    elif input_dict['dragon'] in ['Thor', 'Giovanni', 'Shishimai']:
        errlist.append('requested dragon is not implemented')
    if 'mode' not in input_dict:
        errlist.append('"mode" is a mandatory field')
    if 'transform time' not in input_dict:
        errlist.append('"transform time" is a mandatory field')
    if 'skill' not in input_dict:
        errlist.append('"skill" is a mandatory field')
    if 'stats' not in input_dict:
        errlist.append('"stats" is a mandatory field')
    if errlist:
        return errlist
    reqstats = ['basestr', 
                'passivestr', 
                'activestr',
                'coabstr',
                'passiveskd',
                'activeskd',
                'coabskd',
                'passivefs',
                'activefs',
                'coabfs',
                'critchance',
                'critmod',
                'afflicpun',
                'breakmod',
                'breakpun',
                'basedef',
                'defmod',
                'eleres',
                'aspd', 
                'ahst',
                'eleadv',
                'dboost',
                'energized',
                'inspired',
                'broken',
                'bog',
                'bufftime']
    for stat in reqstats:
        if stat not in input_dict['stats']:
            if stat in ['energized', 'inspired', 'broken', 'bog']:
                input_dict['stats'][stat] = False
            elif stat in ['eleadv', 'dboost']:
                input_dict['stats'][stat] = 1
            elif stat == 'basestr':
                input_dict['stats'][stat] = 1000
            else:
                input_dict['stats'][stat] = 0
    if 'relax' not in input_dict:
        input_dict['relax'] = False
    if 'leniency' not in input_dict:
        input_dict['leniency'] = 0
    return False


if __name__ == "__main__":
    faux_infoset = {
        'dragon' : 'Poliʻahu',
        'mode' : 'effmod',
        'relax' : False,
        'leniency' : 0,
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
    
    solve(faux_infoset)
