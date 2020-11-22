import numpy as np
# from lpsolve55 import *
# from lp_maker import lp_maker
import mip

# testm = mip.Model()
# def translate(x):
#     if x == '==':
#         return 0
#     if x == '<=':
#         return -1
#     if x == '>=':
#         return 1

# NOTE: right now this function is just temporary to ensure that mip
#       will work the way I want - the modeling options mip provides
#       will eventually replace a lot of the setup and functionality
#       currently in place. 
def get_lp_solution(template, time_vec, damage_vec):
    model = mip.Model(sense=mip.MAXIMIZE)
    state_tree = template['state tree']
    constraints = template['constraints']
    # print(constraints)
    length = template['state tree']['size']
    rhs = template['rhs']
    # print(rhs)
    direction = template['direction']
    varrange = [0]*len(damage_vec)
    for state in state_tree:
        if state == 'size':
            continue
        for move in state_tree[state]:
            i = state_tree[state][move]
            # print(f'{state} {move} : {i}, {damage_vec[i]}')
            varrange[i] = model.add_var(name=state+move, obj=damage_vec[i], var_type=mip.INTEGER)
    for i in range(len(constraints)):
        if direction[i] == '<=':
            model += mip.xsum(constraints[i, j]*varrange[j] for j in range(length)) <= rhs[i]
        elif direction[i] == '==':
            model += mip.xsum(constraints[i, j]*varrange[j] for j in range(length)) == rhs[i]
        elif direction[i] == '>=':
            model += mip.xsum(constraints[i, j]*varrange[j] for j in range(length)) >= rhs[i]
    #     print(rhs[i])
    # print(damage_vec)
    # print(model.objective)
    # for i in range(len(constraints)):
    #     print(model.constr_by_name(str(i)))
    
    model.max_mip_gap = 0.01
    model.optimize()
    max_damage = model.objective_value
    model += mip.xsum(damage_vec[j]*varrange[j] for j in range(length)) == max_damage
    model.objective = mip.minimize(mip.xsum(time_vec[j]*varrange[j] for j in range(length)))
    model.optimize()
    min_frames = model.objective_value
    # print(get_transform_frames(min_frames, dragon, template['state tree'], time_vec, getIndex))
    solution = {}
    for v in model.vars:
       if abs(v.x) > 1e-6: # only printing non-zeros
          solution[v.name] = v.x
    return max_damage, min_frames, solution



    
    # intvars = list(range(0, template['state tree']['size']))
    # # direction = [translate(x) for x in template['direction']]
    # lp1 = make_lp(damage_vec, template['constraints'], template['rhs'], direction, integrality=intvars)
    # # lpsolve('solve', lp1)
    # max_damage = lpsolve('get_objective', lp1)

    # direction.append(0)
    # template['rhs'].append(max_damage)
    # new_constr = np.vstack([template['constraints'], damage_vec])
    # lp2 = make_lp(time_vec, new_constr, template['rhs'], direction, integrality=intvars, setminim=True)
    # lpsolve('solve', lp2)
    # min_frames = lpsolve('get_objective', lp2)
    # solution = lpsolve('get_variables', lp2)[0]

    # lpsolve('delete_lp', lp1)
    # lpsolve('delete_lp', lp2)

    # return max_damage, min_frames, solution
    
# def make_lp(objective, constraints, rhs, direction, lowbound=[], ubound=[], integrality=[], scalemode=0, setminim=False):
#     m = len(constraints)
#     n = len(constraints[0])
#     # lp = lpsolve('make_lp', 5, 5)
#     # lpsolve('delete_lp', lp)
#     lpsolve('set_verbose', lp, 'IMPORTANT')
#     lpsolve('set_mat', lp, constraints)
#     lpsolve('set_rh_vec', lp, rhs)
#     lpsolve('set_obj_fn', lp, objective)
#     if not setminim:
#         lpsolve('set_maxim', lp)

#     for i in range(m):
#         if direction[i] < 0:
#             con_type = LE
#         elif direction[i] == 0:
#             con_type = EQ
#         else:
#             con_type = GE
#         lpsolve('set_constr_type', lp, i + 1, con_type)

#     if lowbound:
#         for i in range(n):
#             lpsolve('set_lowbo', lp, i + 1, lowbound[i])
#     if ubound:
#         for i in range(n):
#             lpsolve('set_upbo', lp, i + 1, ubound[i])
    
#     if integrality:
#         for i in integrality:
#             lpsolve('set_int', lp, i, 1)

#     if scalemode:
#         lpsolve('set_scaling', lp, scalemode)

#     return lp

# # if __name__ == "__main__":
# #     make_lp(0, 0, 0, 0)