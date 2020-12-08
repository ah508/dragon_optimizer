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
    solution = {
        'max damage' : 0,
        'min r_frames' : 0,
        'min d_frames' : 0,
        'dps' : 0,
        'decision variables' : {} 
    }

    # testpath = os.getcwd() + '/lptemplates/lpfiles/TESTING.lp'
    model.objective = mip.maximize(mip.xsum(state_values['damage'][i]*varrange[i] for i in range(size)))
    # model.write(testpath) # a test file for debugging
    if not output:
        model.verbose = 0
    model.optimize(relax=relaxation) # right here is where you'd change model properties for speed
    solution['max damage'] = model.objective_value
    if min_frames:
        model += mip.xsum(state_values['damage'][i]*varrange[i] for i in range(size)) == solution['max damage']
        model.objective = mip.minimize(mip.xsum(state_values['realframes'][i]*varrange[i] for i in range(size)))
        model.optimize(relax=relaxation)
    for i in range(size):
       if abs(varrange[i].x) > 1e-6: # only non-zeros
          solution['decision variables'][varrange[i].name] = varrange[i].x
          solution['min r_frames'] += varrange[i].x*state_values['realframes'][i]
          solution['min d_frames'] += varrange[i].x*state_values['frames'][i]
    solution['dps'] = round((60*solution['max damage']/solution['min r_frames']), 2)
    if output:
        print('solution:')
        for v in model.vars:
            if abs(v.x) > 1e-6: # only printing non-zeros
                print('{} : {}'.format(v.name, v.x))
        print(model.status)
        print('damage: {}'.format(solution['max damage']))
        print('realtime: {}'.format(solution['min r_frames']))
        print('dragtime: {}'.format(solution['min d_frames']))
        print('dps: {}'.format(solution['dps']))
    return solution