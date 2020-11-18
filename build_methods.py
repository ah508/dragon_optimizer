import numpy as np
import json
import os

def make_getIndex(tree):
    def getIndex(state, varname):
        return tree[state][varname]
    return getIndex

def map_dict(old_dict, mapping):
    '''Provides re-keying for specific nested keys in a dict.

    Maps a dictionary to a different dictionary with identical values,
    but differing keys. If a mapping is not provided, defaults to the
    original key-value pair. Right now this is exclusively for the
    second set of keys in a nested dictionary with a known format, but
    may be generalized at a later date.

    Parameters
    ----------
    old_dict : { }
        The dictionary to be re-keyed.
    mapping: { }
        A dictionary mapping from old to new keys.
    
    Returns
    -------
    new_dict: { }
        A dictionary identical to old_dict, but with different key names.
    '''

    new_dict = {}
    for k, v in old_dict.items():
        if k == 'size':
            new_dict[k] = v
            continue
        new_dict[k] = {}
        for k2, v2 in v.items():
            try:
                new_dict[k][mapping[k2]] = v2
            except KeyError:
                new_dict[k][k2] = v2
    return new_dict

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
    tree['size'] = index - 1
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
        self.constraints[self.getIndex('Normal', 'T')] = 1
        self.direction = ['==']
        self.rhs = [1]

    def add_const(self, states, moves, values, direct, rhside):
        constr = np.zeros(self.objlen)
        self.direction.append(direct)
        self.rhs.append(rhside)
        for i in range(0, len(states)):
            constr[self.getIndex(states[i], moves[i])] = values[i]
        self.constraints = np.vstack(self.constraints, constr)

    def to_file(self, tag):
        outbound = {
            'name' : tag,
            'state tree' : self.obj,
            'constraints' : self.constraints,
            'direction' : self.direction,
            'rhs' : self.rhs
        }

        filepath = os.getcwd() + '/lptemplates/' + tag
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(outbound, f, cls=NumpyEncoder)