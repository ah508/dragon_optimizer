from build_methods import n_stair, one_d_stair, two_d_stair

def generate_no_boosts(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    for i in range(1, n_attacks-1):
        constraint_class.add_rule('Normal', i, ['Normal', 'Normal', 'Normal'], [i+1, 'D', 'S'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', n_attacks, ['Normal', 'Normal', 'Normal'], ['W', 'D', 'S'])
    constraint_class.add_rule('Normal', 'S', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'W', ['Normal'], [1])
    constraint_class.convert_rules(d_map)

    n_stair(constraint_class, n_attacks)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S'], [1, -1, -1, -1], '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal']])
    constraint_class.add_instruct(['Normal'], moves + ['W', 'D', 'S'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

#NOTE: may not account for frames in framevector
def generate_single_boosts(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    for i in range(1, n_attacks-1):
        constraint_class.add_rule('Normal', i, ['Normal', 'Normal', 'Normal'], [i+1, 'D', 'S'])
        constraint_class.add_rule('Boost1_1', i, ['Boost1_1', 'Boost1_1', 'Exit1_1'], [i+1, 'D', i])
        constraint_class.add_rule('Exit1_1', i, ['Normal', 'Normal'], [i+1, 'D'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', n_attacks, ['Normal', 'Normal', 'Normal'], ['W', 'D', 'S'])
    constraint_class.add_rule('Boost1_1', n_attacks, ['Boost1_1', 'Boost1_1', 'Exit1_1'], ['W', 'D', n_attacks])
    constraint_class.add_rule('Exit1_1', n_attacks, ['Normal', 'Normal'], ['W', 'D'])
    constraint_class.add_rule('Normal', 'S', ['Boost1_1'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'W', ['Normal'], [1])
    constraint_class.add_rule('Boost1_1', 'D', ['Boost1_1'], [1])
    constraint_class.add_rule('Boost1_1', 'W', ['Boost1_1'], [1])
    constraint_class.convert_rules(d_map)        
    
    constraint_class.set_boost('S', 1)
    one_d_stair(constraint_class, n_attacks, 'Normal', 'Exit1_1', -1)
    one_d_stair(constraint_class, n_attacks, 'Boost1_1', 'Exit1_1', 1)
    constraint_class.add_const(['Normal', 'Normal', 'Normal'], [1, 'W', 'D'], [1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Boost1_1', 'Boost1_1', 'Boost1_1'], ['S', 1, 'W', 'D'], [-1, 1, -1, -1], '<=', 0)
    constraint_class.add_const(['Exit1_1', 'Exit1_1', 'Exit1_1'], list(range(1, n_attacks+1)), [1] * n_attacks, '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal'], ['Boost1_1']])
    constraint_class.add_instruct(['Normal', 'Boost1_1'], moves + ['W', 'D'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Boost1_1'], moves + ['W', 'D'], 'frames', '<=', 'buff duration')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_two_boosts(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    # jesus christ I hope I didn't bugger this up
    # an even higher degree of automation would be welcome, but I feel like
    # it would make it harder to find bugs
    # on the other hand, it would make bugs less likely
    # on the other other hand... 
    for i in range(1, n_attacks-1):
        constraint_class.add_rule('Normal', i, ['Normal', 'Normal', 'Normal'], [i+1, 'D', 'S'])
        constraint_class.add_rule('Boost1_1', i, ['Boost1_1', 'Boost1_1', 'Boost1_1', 'Exit1_1'], [i+1, 'D', 'S', i])
        constraint_class.add_rule('Exit1_1', i, ['Post1_1', 'Post1_1', 'Post1_1'], [i+1, 'D', 'S'])
        constraint_class.add_rule('Post1_1', i, ['Post1_1', 'Post1_1', 'Post1_1'], [i+1, 'D', 'S'])
        constraint_class.add_rule('Boost1_2', i, ['Boost1_2', 'Boost1_2', 'Exit1_2'], [i+1, 'D', i])
        constraint_class.add_rule('Exit1_2', i, ['Normal', 'Normal'], [i+1, 'D'])
        constraint_class.add_rule('Boost2_1', i, ['Boost2_1', 'Boost2_1', 'Exit2_1'], [i+1, 'D', i])
        constraint_class.add_rule('Exit2_1', i, ['Boost1_3', 'Boost1_3'], [i+1, 'D'])
        constraint_class.add_rule('Boost1_3', i, ['Boost1_3', 'Boost1_3', 'Exit1_3'], [i+1, 'D', i])
        constraint_class.add_rule('Exit1_3', i, ['Normal', 'Normal'], [i+1, 'D'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', n_attacks, ['Normal', 'Normal', 'Normal'], ['W', 'D', 'S'])
    constraint_class.add_rule('Boost1_1', n_attacks, ['Boost1_1', 'Boost1_1', 'Boost1_1', 'Exit1_1'], ['W', 'D', 'S', n_attacks])
    constraint_class.add_rule('Exit1_1', n_attacks, ['Post1_1', 'Post1_1', 'Post1_1'], ['W', 'D', 'S'])
    constraint_class.add_rule('Post1_1', n_attacks, ['Post1_1', 'Post1_1', 'Post1_1'], ['W', 'D', 'S'])
    constraint_class.add_rule('Boost1_2', n_attacks, ['Boost1_2', 'Boost1_2', 'Exit1_2'], ['W', 'D', n_attacks])
    constraint_class.add_rule('Exit1_2', n_attacks, ['Normal', 'Normal'], ['W', 'D'])
    constraint_class.add_rule('Boost2_1', n_attacks, ['Boost2_1', 'Boost2_1', 'Exit2_1'], ['W', 'D', n_attacks])
    constraint_class.add_rule('Exit2_1', n_attacks, ['Boost1_3', 'Boost1_3'], ['W', 'D'])
    constraint_class.add_rule('Boost1_3', n_attacks, ['Boost1_3', 'Boost1_3', 'Exit1_3'], ['W', 'D', n_attacks])
    constraint_class.add_rule('Exit1_3', n_attacks, ['Normal', 'Normal'], ['W', 'D'])
    constraint_class.add_rule('Normal', 'S', ['Boost1_1'], [1])
    constraint_class.add_rule('Boost1_1', 'S', ['Boost2_1'], [1])
    constraint_class.add_rule('Post1_1', 'S', ['Boost1_2'], [1])
    for somestate in ['Normal', 'Boost1_1', 'Post1_1', 'Boost1_2', 'Boost2_1', 'Boost1_3']:
        constraint_class.add_rule(somestate, 'D', [somestate], [1])
        constraint_class.add_rule(somestate, 'W', [somestate], [1])
    constraint_class.convert_rules(d_map)     

    constraint_class.set_boost('S', 2)
    two_d_stair(constraint_class, n_attacks, 'Normal', 'Exit1_2', -1, 'Exit1_3', -1)
    one_d_stair(constraint_class, n_attacks, 'Boost1_1', 'Exit1_1', 1)
    one_d_stair(constraint_class, n_attacks, 'Post1_1', 'Exit1_1', -1)
    one_d_stair(constraint_class, n_attacks, 'Boost1_2', 'Exit1_2', 1)
    one_d_stair(constraint_class, n_attacks, 'Boost2_1', 'Exit2_1', 1)
    two_d_stair(constraint_class, n_attacks, 'Boost1_3', 'Exit2_1', -1, 'Exit1_3', 1)

    constraint_class.add_const(['Normal', 'Normal', 'Normal'], [1, 'W', 'D'], [1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Boost1_1', 'Boost1_1', 'Boost1_1'], ['S', 1, 'W', 'D'], [-1, 1, -1, -1], '<=', 0)
    constraint_class.add_const(['Post1_1', 'Post1_1', 'Post1_1'], [1, 'W', 'D'], [1, -1, -1], '<=', 0)
    constraint_class.add_const(['Post1_1', 'Boost1_2', 'Boost1_2', 'Boost1_2'], ['S', 1, 'W', 'D'], [-1, 1, -1, -1], '<=', 0)
    constraint_class.add_const(['Boost1_1', 'Boost2_1', 'Boost2_1', 'Boost2_1'], ['S', 1, 'W', 'D'], [-1, 1, -1, -1], '<=', 0)
    constraint_class.add_const(['Boost1_3', 'Boost1_3', 'Boost1_3'], [1, 'W', 'D'], [1, -1, -1], '<=', 0)

    constraint_class.add_const(['Exit1_1', 'Exit1_1', 'Exit1_1', 'Exit2_1', 'Exit2_1', 'Exit2_1'], 
                (list(range(1, n_attacks+1)) + list(range(1, n_attacks+1))),
                [1] * n_attacks*2,
                '<=',
                1)
    constraint_class.add_const(['Exit1_2', 'Exit1_2', 'Exit1_2', 'Exit1_3', 'Exit1_3', 'Exit1_3'], 
                (list(range(1, n_attacks+1)) + list(range(1, n_attacks+1))),
                [1] * n_attacks*2,
                '<=',
                1)

    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal', 'Post1_1'], ['Boost1_1', 'Boost1_2', 'Boost1_3'], ['Boost2_1']])

    constraint_class.add_instruct(['Boost1_1'], moves + ['W', 'D', 'S'], 'realframes', '<=', 'buff duration')
    constraint_class.add_instruct(['Boost1_2'], moves + ['W', 'D'], 'frames', '<=', 'buff duration')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 1)
    constraint_class.add_instruct(['Boost1_1', 'Post1_1'], ['S'], 'skill', '<=', 1)

    constraint_class.add_instruct(
        ['Normal', 'Boost1_1', 'Post1_1', 'Boost1_2', 'Boost2_1', 'Boost1_3'], 
        moves + ['W', 'D'],
        'frames',
        '<=',
        'transform_time'
    )
    constraint_class.add_instruct(
        ['Boost1_1'], 
        moves + ['W', 'D', 'S'], 
        'realframes', 
        '==', 
        0,
        preset=[{
            'state' : 'BuffDummy',
            'move' : 'B1',
            'value' : -1
        }]
    )
    constraint_class.add_instruct(
        ['Boost2_1'], 
        moves + ['W', 'D'], 
        'frames', 
        '<=', 
        'buff duration',
        preset=[{
            'state' : 'BuffDummy',
            'move' : 'B1',
            'value' : 1
        }]
    )
    constraint_class.add_instruct(
        ['Boost1_3'], 
        moves + ['W', 'D'], 
        'frames', 
        '<=', 
        0,
        preset=[{
            'state' : 'BuffDummy',
            'move' : 'B1',
            'value' : -1
        }]
    )
    constraint_class.add_instruct(
        ['Boost1_1'], 
        moves + ['W', 'D'], 
        'sp', 
        '<=', 
        0,
        preset=[{
            'state' : 'Boost1_1',
            'move' : 'S',
            'value' : 30
        }]
    )
    constraint_class.add_instruct(
        ['Boost1_1', 'Post1_1'], 
        moves + ['W', 'D'], 
        'sp', 
        '<=', 
        0,
        preset=[{
            'state' : 'Post1_1',
            'move' : 'S',
            'value' : 30
        }]
    )

    constraint_class.to_file(file_name)

def generate_styx(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    for i in range(1, n_attacks-1):
        constraint_class.add_rule('Normal', i, ['Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal'], [i+1, 'D', 'S0', 'S1', 'S2', 'S3'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S0'])
    constraint_class.add_rule('Normal', n_attacks, ['Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal'], ['W', 'D', 'S0', 'S1', 'S2', 'S3'])
    constraint_class.add_rule('Normal', 'S0', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'S1', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'S2', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'S3', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'W', ['Normal'], [1])
    constraint_class.convert_rules(d_map)

    n_stair(constraint_class, n_attacks)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S0', 'S1', 'S2', 'S3'], [1, -1, -1, -1, -1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Normal'], [3, 'S1'], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], [3, 'S2'], [-1, 2], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], [3, 'S3'], [-1, 3], '<=', 0)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal']])
    constraint_class.add_instruct(['Normal'], moves + ['W', 'D', 'S0', 'S1', 'S2', 'S3'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S0', 'S1', 'S2', 'S3'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_supmym(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    for i in range(1, n_attacks-1):
        constraint_class.add_rule('Normal', i, ['Normal', 'Normal', 'Normal'], [i+1, 'D', 'S'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', n_attacks, ['Normal', 'Normal', 'Normal'], ['W', 'D', 'S'])
    constraint_class.add_rule('Normal', 'S', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'W', ['Normal'], [1])
    constraint_class.convert_rules(d_map)

    constraint_class.set_boost('T', 1)
    n_stair(constraint_class, n_attacks)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S'], [1, -1, -1, -1], '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform'], ['Normal']])
    constraint_class.add_instruct(['Normal'], moves + ['W', 'D', 'S'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_c3_delay(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    constraint_class.add_rule('Normal', 1, ['Normal', 'Normal', 'Normal'], [2, 'D', 'S'])
    constraint_class.add_rule('Normal', 2, ['Normal', 'Normal', 'Normal'], [3, 'D', 'S'])
    constraint_class.add_rule('Normal', 3, ['Normal', 'Normal', 'Normal', 'Normal', 'Normal'], [4, 'D', 'W', 'C3_skl', 'C3_end'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', 'C3_skl', ['Normal'], ['S'])
    constraint_class.add_rule('Normal', 'C3_end', [], [])
    constraint_class.add_rule('Normal', 'S', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'W', ['Normal'], [1])
    constraint_class.convert_rules(d_map)

    # in place of normal staircase:
    constraint_class.add_const(['Normal', 'Normal'], [1, 2], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], [2, 3], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [3, 'W', 'C3_skl', 'C3_end'], [-1, 1, 1, 1], '<=', 0)

    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S'], [1, -1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Normal'], ['S', 'C3_skl'], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal'], ['C3_end'], [1], '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal']])
    constraint_class.add_instruct(['Normal'], moves + ['C3_skl', 'C3_end', 'W', 'D', 'S'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_hbh(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    constraint_class.add_rule('Normal', 1, ['Normal', 'Normal', 'Normal'], [2, 'D', 'S'])
    constraint_class.add_rule('Normal', 2, ['Normal', 'Normal', 'Normal'], [3, 'D', 'S'])
    constraint_class.add_rule('Normal', 3, ['Normal', 'Normal', 'Normal'], [4, 'C3a_skl', 'C3a_end'])
    constraint_class.add_rule('Normal', 4, ['Normal', 'Normal', 'Normal', 'Normal', 'Normal'], [3, 'W', 'D', 'C3b_skl', 'C3b_end'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', 'C3a_skl', ['Normal'], ['S'])
    constraint_class.add_rule('Normal', 'C3b_skl', ['Normal'], ['S'])
    constraint_class.add_rule('Normal', 'C3a_end', [], [])
    constraint_class.add_rule('Normal', 'C3b_end', [], [])
    constraint_class.add_rule('Normal', 'S', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'W', ['Normal'], [1])
    constraint_class.convert_rules(d_map) 

    # in place of normal staircase:
    constraint_class.add_const(['Normal', 'Normal'], [1, 2], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], [2, 3], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [3, 4, 'C3a_skl', 'C3a_end'], [-1, 1, 1, 1], '==', 0) #take note of sign
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [4, 'W', 'C3b_skl', 'C3b_end'], [-1, 1, 1, 1], '<=', 0)

    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S'], [1, -1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Normal', 'Normal'], ['S', 'C3a_skl', 'C3b_skl'], [-1, 1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], ['C3a_end', 'C3b_end'], [1, 1], '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal']])
    constraint_class.add_instruct(['Normal'], moves + ['C3a_skl', 'C3a_end', 'C3b_skl', 'C3b_end', 'W', 'D', 'S'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_leviathan(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    constraint_class.add_rule('Normal', 1, ['Normal', 'Normal', 'Normal'], [2, 'D', 'S'])
    constraint_class.add_rule('Boost1_1', 1, ['Boost1_1', 'Boost1_1', 'Exit1_1'], [2, 'D', 1])
    constraint_class.add_rule('Exit1_1', 1, ['Normal', 'Normal'], [2, 'D'])
    constraint_class.add_rule('Normal', 2, ['Normal', 'Normal', 'Normal', 'Normal'], [3, 'D', 'C2_skl', 'C2_end'])
    constraint_class.add_rule('Boost1_1', 2, ['Boost1_1', 'Boost1_1', 'Boost1_1', 'Exit1_1'], [3, 'D', 'C2_end', 2])
    constraint_class.add_rule('Exit1_1', 2, ['Normal', 'Normal'], [3, 'D'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', 3, ['Normal', 'Normal', 'Normal'], ['W', 'D', 'S'])
    constraint_class.add_rule('Boost1_1', 3, ['Boost1_1', 'Boost1_1', 'Exit1_1'], ['W', 'D', 3])
    constraint_class.add_rule('Exit1_1', 3, ['Normal', 'Normal'], ['W', 'D'])
    constraint_class.add_rule('Normal', 'C2_skl', ['Normal'], ['S'])
    constraint_class.add_rule('Normal', 'C2_end', [], [])
    constraint_class.add_rule('Normal', 'S', ['Boost1_1'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'W', ['Normal'], [1])
    constraint_class.add_rule('Boost1_1', 'D', ['Boost1_1'], [1])
    constraint_class.add_rule('Boost1_1', 'W', ['Boost1_1'], [1])
    constraint_class.convert_rules(d_map) 
    
    constraint_class.set_boost('S', 1)

    # in place of normal staircase:
    constraint_class.add_const(['Normal', 'Normal', 'Exit1_1'], [1, 2, 1], [-1, 1, -1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal', 'Exit1_1'], [2, 3, 'C2_skl', 'C2_end', 2], [-1, 1, 1, 1, -1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Exit1_1'], [3, 'W', 3], [-1, 1, -1], '<=', 0)
    # second staircase as per usual:
    one_d_stair(constraint_class, n_attacks, 'Boost1_1', 'Exit1_1', 1)

    constraint_class.add_const(['Normal', 'Normal', 'Normal'], [1, 'W', 'D'], [1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Boost1_1', 'Boost1_1', 'Boost1_1'], ['S', 1, 'W', 'D'], [-1, 1, -1, -1], '<=', 0)
    constraint_class.add_const(['Exit1_1', 'Exit1_1', 'Exit1_1'], list(range(1, n_attacks+1)), [1] * n_attacks, '<=', 1)
    constraint_class.add_const(['Normal', 'Normal'], ['S', 'C2_skl'], [-1, 1], '<=', 0)
    constraint_class.add_const(['Boost1_1'], ['C2_skl'], [1], '==', 0)
    constraint_class.add_const(['Normal', 'Boost1_1'], ['C2_end', 'C2_end'], [1, 1], '<=', 1)

    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal'], ['Boost1_1']])
    constraint_class.add_instruct(['Normal', 'Boost1_1'], moves + ['C2_skl', 'C2_end', 'W', 'D'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Boost1_1'], moves + ['W', 'D'], 'frames', '<=', 'buff duration')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_reborn_pz(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    for i in range(1, n_attacks-1):
        constraint_class.add_rule('Normal', i, ['Normal', 'Normal', 'Normal' 'End'], [i+1, 'D', 'S', 'S'])
    constraint_class.add_rule('Transform', 'T', ['Normal', 'Normal'], [1, 'S'])
    constraint_class.add_rule('Normal', n_attacks, ['Normal', 'Normal', 'End'], ['W', 'D', 'S'])
    constraint_class.add_rule('Normal', 'S', ['Normal'], [1])
    constraint_class.add_rule('Normal', 'D', ['Normal', 'End'], [1, 'S'])
    constraint_class.add_rule('Normal', 'W', ['Normal', 'End'], [1, 'S'])
    constraint_class.add_rule('End', 'S', [], [])
    constraint_class.convert_rules(d_map)

    n_stair(constraint_class, n_attacks)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S'], [1, -1, -1, -1], '<=', 1)
    constraint_class.add_const(['End'], ['S'], [1], '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal', 'End']])
    constraint_class.add_instruct(['Normal'], moves + ['W', 'D', 'S'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)