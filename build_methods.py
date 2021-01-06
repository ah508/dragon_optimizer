import numpy as np
import mip
import json
import os
from pathlib import Path

def make_getIndex(tree):
    def getIndex(state, varname):
        return tree[state][varname]
    return getIndex

def n_stair(ClassInstance, upto):
    for i in range(1, upto):
        ClassInstance.add_const(['Normal', 'Normal'], [i, i+1], [-1, 1], '<=', 0)
    ClassInstance.add_const(['Normal', 'Normal'], [upto, 'W'], [-1, 1], '<=', 0)

def one_d_stair(ClassInstance, upto, state1, d1state, d1):
    for i in range(1, upto):
        ClassInstance.add_const([state1, state1, d1state], [i, i+1, i], [-1, 1, d1], '<=', 0)
    ClassInstance.add_const([state1, state1, d1state], [upto, 'W', upto], [-1, 1, d1], '<=', 0)

def two_d_stair(ClassInstance, upto, state1, d1state, d1, d2state, d2):
    for i in range(1, upto):
        ClassInstance.add_const([state1, state1, d1state, d2state], [i, i+1, i, i], [-1, 1, d1, d2], '<=', 0)
    ClassInstance.add_const([state1, state1, d1state, d2state], [upto, 'W', upto, upto], [-1, 1, d1, d2], '<=', 0)

# def sep_stair(ClassInstance, upto, state1, val1, state2, val2):
#     for i in range(1, upto+1):
#         ClassInstance.add_const([state1, state2], [i, i], [val1, val2], '<=', 0)

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

# class NumpyEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()
#         return json.JSONEncoder.default(self, obj)

class Make_Constraints:
    def __init__(self, obj):
        self.obj = obj
        self.model = mip.Model()
        self.getIndex = make_getIndex(obj)
        self.objlen = obj['size']
        self.constraints = np.zeros(self.objlen)
        self.constraints[self.getIndex('Transform', 'T')] = 1
        self.direction = ['==']
        self.rhs = [1]
        self.instructions = []
        self.state_order = [['Transform', 'Normal']]
        self.boost_on = None
        self.boost_num = 0
        self.rules = {}

    def set_boost(self, boost_on, max_boosts):
        self.boost_on = boost_on
        self.boost_num = max_boosts

    def add_const(self, states, moves, values, direct, rhside):
        constr = np.zeros(self.objlen)
        self.direction.append(direct)
        self.rhs.append(rhside)
        if states:
            for i in range(0, len(states)):
                constr[self.getIndex(states[i], moves[i])] = values[i]
        self.constraints = np.vstack((self.constraints, constr))
        # some will argue that with mip this is redundant and uneccessary
        # while that may be true, I already have the code, and since this
        # is just for the setup scripts, performance isn't my biggest concern

    def remap_dict(self, mapping):
        '''Provides re-keying for specific nested keys in a dict.

        Maps a dictionary to a different dictionary with identical values,
        but differing keys. If a mapping is not provided, defaults to the
        original key-value pair. Right now this is exclusively for the
        second set of keys in a nested dictionary with a known format, but
        may be generalized at a later date.

        Parameters
        ----------
        mapping: { }
            A dictionary mapping from old to new keys.
        
        Returns
        -------
        None. This method modifies attributes of the class.
        '''

        new_dict = {}
        for k, v in self.obj.items():
            if k == 'size':
                new_dict[k] = v
                continue
            new_dict[k] = {}
            for k2, v2 in v.items():
                try:
                    new_dict[k][mapping[k2]] = v2
                except KeyError:
                    new_dict[k][k2] = v2
        self.obj = new_dict

    def make_vars(self):
        self.varrange = [0]*self.objlen
        for state in self.obj:
            if state == 'size':
                continue
            for move in self.obj[state]:
                i = self.obj[state][move]
                self.varrange[i] = self.model.add_var(name=state+move, var_type=mip.INTEGER)
        self.model.objective = mip.xsum(1*self.varrange[i] for i in range(self.objlen))

    def constr_to_mip(self):
        for i in range(len(self.constraints)):
            if self.direction[i] == '<=':
                self.model += (
                    mip.xsum(self.constraints[i, j]*self.varrange[j] for j in range(self.objlen)) 
                    <= self.rhs[i]
                )
            elif self.direction[i] == '==':
                self.model += (
                    mip.xsum(self.constraints[i, j]*self.varrange[j] for j in range(self.objlen)) 
                    <= self.rhs[i]
                )
            elif self.direction[i] == '>=':
                self.model += (
                    mip.xsum(self.constraints[i, j]*self.varrange[j] for j in range(self.objlen)) 
                    <= self.rhs[i]
                )
    
    def new_state_order(self, states):
        self.state_order = states

    def add_instruct(self, states, moves, cvalue, direction, rhsvalue, preset=[]):#, omit, boostnum):
        # NOTE: states must be strictly ordered
        # NOTE: first instruction must *always* list states in order of
        self.instructions.append({
            'states' : states,       # a vector of states where these apply
            'moves' : moves,         # the moves in each state that are affected
            'input type' : cvalue,   # 'frames', 'sp', 'realframes' 
            'direction' : direction, # '<=', '==', '>='
            'rhs' : rhsvalue,        # 'transform time', 'buff duration', 'skill', 0
            'preset' : preset        # a list of dictionaries {state, move, value}
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

    def add_rule(self, pstate, parent, cstate, children):
        self.rules[parent] = {
            'state' : pstate,
            'children' : children,
            'child states' : cstate
        }

    def convert_rules(self, mapping):
        new_dict = {}
        for k, v in self.rules.items():
            if k in mapping.keys():
                temp_key = mapping[k]
            else:
                temp_key = k
            new_dict[temp_key] = {
                'state' : v['state'],
                'children' : [mapping[val] if val in mapping.keys() else val for val in v['children']],
                'child states' : v['child states']
            }
        self.rules = new_dict

    def to_file(self, tag):
        outbound = {
            'name' : tag,
            'state tree' : self.obj,
            'state order' : self.state_order,
            'instructions' : self.instructions,
            'boost on' : self.boost_on,
            'boost num' : self.boost_num,
            'rules' : self.rules
        }

        # filepath = os.getcwd() + '/lptemplates/'
        filepath = str(Path(__file__).parent) + '/lptemplates/'
        self.model.write(filepath + 'lpfiles/' + tag + '.lp')
        with open(filepath + tag + '.json', 'w', encoding='utf-8') as f:
            json.dump(outbound, f)#, cls=NumpyEncoder)