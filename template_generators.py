from build_methods import n_stair, one_d_stair, two_d_stair

#buffereds go here
#styx goes here
#gala pos goes here

def generate_no_boosts(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

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

    # in place of normal staircase:
    constraint_class.add_const(['Normal', 'Normal'], [1, 2], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], [2, 3], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [3, 'W', 'DUMMY_S', 'DUMMY_E'], [-1, 1, 1, 1], '<=', 0)

    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S'], [1, -1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Normal'], ['S', 'DUMMY_S'], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal'], ['DUMMY_E'], [1], '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal']])
    constraint_class.add_instruct(['Normal'], moves + ['DUMMY_S', 'DUMMY_E', 'W', 'D', 'S'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_hbh(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

    # in place of normal staircase:
    constraint_class.add_const(['Normal', 'Normal'], [1, 2], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], [2, 3], [-1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [3, 4, 'D_Sa', 'D_Ea'], [-1, 1, 1, 1], '==', 0) #take note of sign
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [4, 'W', 'D_Sb', 'D_Eb'], [-1, 1, 1, 1], '<=', 0)

    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal'], [1, 'W', 'D', 'S'], [1, -1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Normal', 'Normal'], ['S', 'D_Sa', 'D_Sb'], [-1, 1, 1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal'], ['D_Ea', 'D_Eb'], [1, 1], '<=', 1)
    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal']])
    constraint_class.add_instruct(['Normal'], moves + ['D_Sa', 'D_Ea', 'D_Sb', 'D_Eb', 'W', 'D', 'S'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_leviathan(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]
    
    constraint_class.set_boost('S', 1)

    # in place of normal staircase:
    constraint_class.add_const(['Normal', 'Normal', 'Exit1_1'], [1, 2, 1], [-1, 1, -1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Normal', 'Normal', 'Exit1_1'], [2, 3, 'DUMMY_S', 'DUMMY_E', 2], [-1, 1, 1, 1, -1], '<=', 0)
    constraint_class.add_const(['Normal', 'Normal', 'Exit1_1'], [3, 'W', 3], [-1, 1, -1], '<=', 0)
    # second staircase as per usual:
    one_d_stair(constraint_class, n_attacks, 'Boost1_1', 'Exit1_1', 1)

    constraint_class.add_const(['Normal', 'Normal', 'Normal'], [1, 'W', 'D'], [1, -1, -1], '<=', 1)
    constraint_class.add_const(['Normal', 'Boost1_1', 'Boost1_1', 'Boost1_1'], ['S', 1, 'W', 'D'], [-1, 1, -1, -1], '<=', 0)
    constraint_class.add_const(['Exit1_1', 'Exit1_1', 'Exit1_1'], list(range(1, n_attacks+1)), [1] * n_attacks, '<=', 1)
    constraint_class.add_const(['Normal', 'Normal'], ['S', 'DUMMY_S'], [-1, 1], '<=', 0)
    constraint_class.add_const(['Boost1_1'], ['DUMMY_S'], [1], '==', 0)
    constraint_class.add_const(['Normal', 'Boost1_1'], ['DUMMY_E', 'DUMMY_E'], [1, 1], '<=', 1)

    constraint_class.remap_dict(d_map)
    constraint_class.make_vars()
    constraint_class.constr_to_mip()
    constraint_class.new_state_order([['Transform', 'Normal'], ['Boost1_1']])
    constraint_class.add_instruct(['Normal', 'Boost1_1'], moves + ['DUMMY_S', 'DUMMY_E', 'W', 'D'], 'frames', '<=', 'transform_time')
    constraint_class.add_instruct(['Boost1_1'], moves + ['W', 'D'], 'frames', '<=', 'buff duration')
    constraint_class.add_instruct(['Normal'], ['S'], 'skill', '<=', 'skill')
    constraint_class.to_file(file_name)

def generate_reborn_pz(constraint_class, n_attacks, d_map, file_name):
    moves = [0] * n_attacks
    for i in range(n_attacks):
        moves[i] = d_map[i+1]

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