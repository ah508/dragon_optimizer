import time
import mip
from marshmallow import Schema, fields, ValidationError
from file_fetchers import fetch_dragon, fetch_key, load_data
from data_refine import generate_state_stats, get_model_variables
from build_methods import make_getIndex
from lp_solver import set_model_constraints, solve_model

def solve(infoset, output=True):
    startttime = time.time()
    model = mip.Model()
    drg = infoset['dragon']
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

# def validate_min(value, minimum='zero'):
#     if minimum == 'zero':
#         if value < 0:
#             raise ValidationError('Value must be non-negative')
#     elif minimum == 'small':
#         if value < 1e-5:
#             raise ValidationError('Value must be greater than zero')

# class InputValidator(Schema):
#     dragon = fields.String(required=True, error_messages={"dragon is required"})


def check_input(input_dict):
    errlist = []
    reqinput = [
        {'id' : 'dragon', 'default' : None, 't' : str},
        {'id' : 'mode', 'default' : None, 't' : str},
        {'id' : 'transform time', 'default' : None, 't' : int},
        {'id' : 'skill', 'default' : 1, 't' : int},
        {'id' : 'stats', 'default' : None, 't' : dict},
        {'id' : 'relax', 'default' : False, 't' : bool},
        {'id' : 'leniency', 'default' : 0, 't' : int}
    ]
    for req in reqinput:
        if req['id'] not in input_dict:
            if req['default'] == None:
                errlist.append('{} is a mandatory input field'.format(req['id']))
            else:
                input_dict[req['id']] = req['default']
        else:
            if not isinstance(input_dict[req['id']], req['t']):
                try:
                    input_dict[req['id']] = req['t'](input_dict[req['id']])
                except ValueError:
                    errlist.append('input {} is not of a valid type.'.format(req['id']))
    banned = [
        'Gala Thor',
        'Giovanni',
        'Shishimai',
        'Horus',
        'Mini Hildy',
        'Mini Zodi',
        'Barbatos'
    ]
    if 'dragon' in input_dict:
        if input_dict['dragon'] in banned:
            errlist.append('{} is not implemented'.format(input_dict['dragon']))
    reqstats = [
        {'id' : 'basestr', 'default' : 1000, 't' : float, 'min' : 0},
        {'id' : 'passivestr', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'activestr', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'coabstr', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'passiveskd', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'activeskd', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'coabskd', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'passivefs', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'activefs', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'coabfs', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'critchance', 'default' : 0, 't' : float, 'min' : 0},
        {'id' : 'critmod', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'afflicpun', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'breakmod', 'default' : 0.6, 't' : float, 'min' : 1e-4},
        {'id' : 'breakpun', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'basedef', 'default' : 10, 't' : float, 'min' : 1e-4},
        {'id' : 'defmod','default' : 0, 't' : float, 'min' : None},
        {'id' : 'eleres', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'aspd', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'ahst', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'eleadv', 'default' : 1, 't' : float, 'min' : 0},
        {'id' : 'dboost', 'default' : 0, 't' : float, 'min' : None},
        {'id' : 'energized', 'default' : False, 't' : bool, 'min' : None},
        {'id' : 'inspired', 'default' : False, 't' : bool, 'min' : None},
        {'id' : 'broken', 'default' : False, 't' : bool, 'min' : None},
        {'id' : 'bog', 'default' : False, 't' : bool, 'min' : None},
        {'id' : 'bufftime', 'default' : 0, 't' : float, 'min' : None}
    ]
    s = 'stats' # this is harder to read, but it's for the sake of brevity
    for stat in reqstats:
        if stat['id'] not in input_dict[s]:
            input_dict[s][stat['id']] = stat['default']
        else:
            if not isinstance(input_dict[s][stat['id']], stat['t']):
                try:
                    input_dict[s][stat['id']] = stat['t'](input_dict[s][stat['id']])
                except ValueError:
                    errlist.append('stat {} is not of a valid type.'.format(stat['id']))
                    continue
            if stat['min'] and input_dict[s][stat['id']] < stat['min']:
                errlist.append('stat {} is below the minimum permitted value of {}'.format(stat['id'], stat['min']))
    if errlist:
        return errlist
    else:
        return False


if __name__ == "__main__":
    faux_infoset = {
        'dragon' : 'High Brunhilda',
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
            'dboost' : 0,
            'energized' : False,
            'inspired' : False,
            'broken' : False,
            'bog' : False,
            'bufftime' : 0
        }
    }
    
    solve(faux_infoset)
