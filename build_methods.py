import numpy as np
import json
import os

def make_getIndex(tree):
    def getIndex(state, varname):
        return tree[state][varname]
    return getIndex

def normal_staircase(ClassInstance, upto):
    for i in range(1, upto):
        ClassInstance.add_const(['Normal', 'Normal'], [i, i+1], [-1, 1], '<=', 0)
    ClassInstance.add_const(['Normal', 'Normal'], [upto, 'W'], [-1, 1], '<=', 0)

def one_dummy_staircase(ClassInstance, upto, d1state, d1):
    for i in range(1, upto):
        ClassInstance.add_const(['Normal', 'Normal', d1state], [i, i+1, i], [-1, 1, d1], '<=', 0)
    ClassInstance.add_const(['Normal', 'Normal', d1state], [upto, 'W', upto], [-1, 1, d1], '<=', 0)

def two_dummy_staircase(ClassInstance, upto, d1state, d1, d2state, d2):
    for i in range(1, upto):
        ClassInstance.add_const(['Normal', 'Normal', d1state, d2state], [i, i+1, i, i], [-1, 1, d1, d2], '<=', 0)
    ClassInstance.add_const(['Normal', 'Normal', d1state, d2state], [upto, 'W', upto, upto], [-1, 1, d1, d2], '<=', 0)

def double_staircase(ClassInstance, upto, state1, val1, state2, val2):
    for i in range(1, upto+1):
        ClassInstance.add_const([state1, state2], [i, i], [val1, val2], '<=', 0)

def build_tree(states, include_all=[]):
    '''Maps strings to the indices of decision variables.

    Intended to ease the construction of LPs and make things
    all around more human readable.

    Parameters
    ----------
    states : { }
        May be either empty, or with keys "omit" and "include_only.
        Determines if the contents of the state vary from default.
    include_all : [ ] (=[ ])
        A list containing keys initialized in every state, unless
        specified otherwise with "omit" or "include_only."

    Returns
    -------
    tree : { }
        A dictionary mapping states and substates to the indices of
        decision variables. Also lists the total number of decision
        variables.
    '''

    index = 0
    tree = {}
    for state in states:
        tree[state] = {}
        if states[state]:
            if states[state]['omit']:
                for move in include_all:
                    if move not in states[state]['omit']:
                        tree[state][move] = index
                        index += 1
            else:
                for move in states[state]['include_only']:
                    tree[state][move] = index
                    index += 1
        else:
            for move in include_all:
                tree[state][move] = index
                index += 1
    tree['size'] = index
    return tree

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Make_Constraints:
    def __init__(self, obj):
        self.obj = obj
        self.getIndex = make_getIndex(obj)
        self.objlen = obj['size']
        self.constraints = np.zeros(self.objlen)
        self.constraints[self.getIndex('Transform', 'T')] = 1
        self.direction = ['==']
        self.rhs = [1]
        self.instructions = []
        self.booston = None

    def set_booston(self, val):
        self.booston = val

    def add_const(self, states, moves, values, direct, rhside):
        constr = np.zeros(self.objlen)
        self.direction.append(direct)
        self.rhs.append(rhside)
        if states:
            for i in range(0, len(states)):
                constr[self.getIndex(states[i], moves[i])] = values[i]
        self.constraints = np.vstack((self.constraints, constr))
    
    def add_instruct(self, state, row, value, omit, boostnum):
        # NOTE: instructions are to be strictly ordered
        self.instructions.append({
            'state' : state,      # any valid state or 'rhs'
            'row' : row,
            'input type' : value, # 'frames', 'sp', 'realframes' | 'transform time', 'buff duration', 'skill'
            'omissions' : omit,   # a list indicating moves to skip, ie: ['W', 'D', 'S']
            'boosts' : boostnum,  # the number of boosts present for this state
        })
        # presence of skill       [-1]
        # total frames            [-2]
        # buff frames             [-3]
        # buff frames 2           [-4]
        # buff frames 3 (overlap) [-5]
        # buff frames 4           [-6]
        # sp 1                    [-7]
        # sp 2                    [-8]
        # overlap 1               [-9]
        # overlap 2               [-10]
        # second skill selection  [-11]
    

    def to_file(self, tag):
        outbound = {
            'name' : tag,
            'state tree' : self.obj,
            'constraints' : self.constraints,
            'direction' : self.direction,
            'rhs' : self.rhs,
            'instructions' : self.instructions,
            'boost on' : self.booston
        }

        filepath = os.getcwd() + '/lptemplates/' + tag +'.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(outbound, f, cls=NumpyEncoder)