import numpy as np
from lpsolve55 import *
from lp_maker import lp_maker

def translate(x):
    if x == '==':
        return 0
    if x == '<=':
        return -1
    if x == '>=':
        return 1

def get_lp_solution(template, time_vec, damage_vec):
    integrality = list(range(0, template['state tree']['size']))
    direction = [translate(x) for x in template['direction']]
    lp1 = lp_maker(damage_vec, template['constraints'], template['rhs'], direction, xint=integrality)
    lpsolve('solve', lp1)
    max_damage = lpsolve('get_objective', lp1)

    direction.append(0)
    template['rhs'].append(max_damage)
    new_constr = np.vstack([template['constraints'], damage_vec])
    lp2 = lp_maker(time_vec, new_constr, template['rhs'], direction, xint=integrality)
    lpsolve('solve', lp2)
    min_frames = lpsolve('get_objective', lp2)
    solution = lpsolve('get_variables', lp2)[0]

    lpsolve('delete_lp', lp1)
    lpsolve('delete_lp', lp2)

    return max_damage, min_frames, solution
    
