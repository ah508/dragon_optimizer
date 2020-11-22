import numpy as np
from lpsolve55 import *
from lp_maker import lp_maker
# import mip

# testm = mip.Model()
# def translate(x):
#     if x == '==':
#         return 0
#     if x == '<=':
#         return -1
#     if x == '>=':
#         return 1

def get_lp_solution(template, time_vec, damage_vec):
    intvars = list(range(0, template['state tree']['size']))
    direction = [translate(x) for x in template['direction']]
    lp1 = make_lp(damage_vec, template['constraints'], template['rhs'], direction, integrality=intvars)
    lpsolve('solve', lp1)
    max_damage = lpsolve('get_objective', lp1)

    direction.append(0)
    template['rhs'].append(max_damage)
    new_constr = np.vstack([template['constraints'], damage_vec])
    lp2 = make_lp(time_vec, new_constr, template['rhs'], direction, integrality=intvars, setminim=True)
    lpsolve('solve', lp2)
    min_frames = lpsolve('get_objective', lp2)
    solution = lpsolve('get_variables', lp2)[0]

    lpsolve('delete_lp', lp1)
    lpsolve('delete_lp', lp2)

    return max_damage, min_frames, solution
    
def make_lp(objective, constraints, rhs, direction, lowbound=[], ubound=[], integrality=[], scalemode=0, setminim=False):
    m = len(constraints)
    n = len(constraints[0])
    # lp = lpsolve('make_lp', 5, 5)
    # lpsolve('delete_lp', lp)
    lpsolve('set_verbose', lp, 'IMPORTANT')
    lpsolve('set_mat', lp, constraints)
    lpsolve('set_rh_vec', lp, rhs)
    lpsolve('set_obj_fn', lp, objective)
    if not setminim:
        lpsolve('set_maxim', lp)

    for i in range(m):
        if direction[i] < 0:
            con_type = LE
        elif direction[i] == 0:
            con_type = EQ
        else:
            con_type = GE
        lpsolve('set_constr_type', lp, i + 1, con_type)

    if lowbound:
        for i in range(n):
            lpsolve('set_lowbo', lp, i + 1, lowbound[i])
    if ubound:
        for i in range(n):
            lpsolve('set_upbo', lp, i + 1, ubound[i])
    
    if integrality:
        for i in integrality:
            lpsolve('set_int', lp, i, 1)

    if scalemode:
        lpsolve('set_scaling', lp, scalemode)

    return lp

# if __name__ == "__main__":
#     make_lp(0, 0, 0, 0)