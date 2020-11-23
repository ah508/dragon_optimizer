import mip

def get_constraint(instruction, state_tree, state_values, getIndex):
    constraint = [0] * state_tree['size']
    input_type = instruction['input type']
    print(input_type)
    switch_c = -1 if input_type == 'sp' else 1
    if instruction['states']:
        for state in instruction['states']:
            for move in instruction['moves']:
                index = getIndex(state, move)
                print(index)
                if move == 'S':
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
        rhs = state_values[instruction['rhs']]
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

def solve_model(model, varrange, state_values, min_frames=True):
    size = len(varrange)
    solution = {
        'max damage' : 0,
        'min r_frames' : 0,
        'min d_frames' : 0,
        'dps' : 0,
        'decision variables' : {} 
    }

    model.max_mip_gap = 0.01
    model.objective = mip.maximize(mip.xsum(state_values['damage'][i]*varrange[i] for i in range(size)))
    model.optimize()
    solution['max damage'] = model.objective_value
    if min_frames:
        model += mip.xsum(state_values['damage'][i]*varrange[i] for i in range(size)) == solution['max damage']
        model.objective = mip.minimize(mip.xsum(state_values['realframes'][i]*varrange[i] for i in range(size)))
        model.optimize()
    for i in range(size):
       if abs(varrange[i].x) > 1e-6: # only non-zeros
          solution['decision variables'][varrange[i].name] = varrange[i].x
          solution['min r_frames'] += varrange[i].x*state_values['realframes'][i]
          solution['min d_frames'] += varrange[i].x*state_values['frames'][i]
    solution['dps'] = round((60*solution['max damage']/solution['min r_frames']), 2)
    print('solution:')
    for v in model.vars:
       if abs(v.x) > 1e-6: # only printing non-zeros
          print('{} : {}'.format(v.name, v.x))
    return solution