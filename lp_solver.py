import mip
# import os

def get_constraint(instruction, state_tree, state_values, getIndex):
    constraint = [0] * state_tree['size']
    input_type = instruction['input type']
    switch_c = -1 if input_type == 'sp' else 1
    if instruction['states']:
        for state in instruction['states']:
            for move in instruction['moves']:
                index = getIndex(state, move)
                if move.startswith('S') and input_type == 'skill':
                    constraint[index] = 1
                else:
                    constraint[index] = (switch_c*state_values[input_type][index])
    if instruction['preset']:
        for setting in instruction['preset']:
            index = getIndex(setting['state'], setting['move'])
            constraint[index] = setting['value']
    return constraint

def set_model_constraints(model, varrange, template, state_values, getIndex):
    obj_len = template['state tree']['size']
    for instruction in template['instructions']:
        if isinstance(instruction['rhs'], str):
            if state_values[instruction['rhs']] == 'inf':
                continue
            rhs = state_values[instruction['rhs']]
        else:
            rhs = instruction['rhs']
        constraint = get_constraint(instruction, 
                                    template['state tree'], 
                                    state_values, 
                                    getIndex)
        if instruction['direction'] == '<=':
            model += mip.xsum(constraint[i]*varrange[i] for i in range(obj_len)) <= rhs
        elif instruction['direction'] == '==':
            model += mip.xsum(constraint[i]*varrange[i] for i in range(obj_len)) == rhs
        elif instruction['direction'] == '>=':
            model += mip.xsum(constraint[i]*varrange[i] for i in range(obj_len)) >= rhs

def solve_model(model, varrange, state_values, min_frames=True, output=True, relaxation=False):
    size = len(varrange)
    max_damage = 0
    min_r_frames = 0
    min_d_frames = 0
    dps = 0
    solution = {
        'dataTable' : [],
        'decisionVariables' : []
    }
    # testpath = os.getcwd() + '/lptemplates/lpfiles/TESTING.lp'
    model.objective = mip.maximize(mip.xsum(state_values['damage'][i]*varrange[i] for i in range(size)))
    # model.write(testpath) # a test file for debugging
    if not output:
        model.verbose = 0
    model.optimize(relax=relaxation) # right here is where you'd change model properties for speed
    if model.status not in [mip.OptimizationStatus.OPTIMAL]:
        print(model.status)
        solution['dataTable'].append({'id' : 'status', 'value' : 'INFEASIBLE'})
        solution['decisionVariables'].append({'id' : 'N/A', 'value' : 'N/A'})
        return solution
    max_damage = model.objective_value
    if min_frames:
        model += mip.xsum(state_values['damage'][i]*varrange[i] for i in range(size)) == max_damage
        model.objective = mip.minimize(mip.xsum(state_values['realframes'][i]*varrange[i] for i in range(size)))
        model.optimize(relax=relaxation)
    for i in range(size):
        if abs(varrange[i].x) > 1e-6: # only non-zeros
          solution['decisionVariables'].append({'id' : [varrange[i].name], 'value' : varrange[i].x})
          min_r_frames += varrange[i].x*state_values['realframes'][i]
          min_d_frames += varrange[i].x*state_values['frames'][i]
    if min_r_frames <= 0:
        dps = 0
    else:
        dps = round((60*max_damage/min_r_frames), 2)

    solution['dataTable'].append({'id' : 'max damage', 'value' : max_damage})
    solution['dataTable'].append({'id' : 'real time', 'value' : min_r_frames})
    solution['dataTable'].append({'id' : 'dragon time', 'value' : min_d_frames})
    solution['dataTable'].append({'id' : 'dps', 'value' : dps})
    if output:
        print('solution:')
        for v in model.vars:
            if abs(v.x) > 1e-6: # only printing non-zeros
                print('{} : {}'.format(v.name, v.x))
        print(model.status)
        for statistic in solution['dataTable']:
            print('{:11} : {:10}'.format(statistic['id'], statistic['value']))
    return solution