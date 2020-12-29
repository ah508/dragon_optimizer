# __all__ isn't needed here
# these are dictionaries to be used in the setup scripts to generate templates
NO_BOOST = {
    'Transform' : {
        'omit' : [],
        'include_only' : ['T']
    },
    'Normal' : {}
}

ONE_S_BOOST = {
    'Transform' : {
        'omit' : [],
        'include_only' : ['T']
    },
    'Normal' : {},
    'Boost1_1' : {
        'omit' : ['S']
    },
    'Exit1_1' : {
        'omit' : ['W', 'D', 'S'],
    },
}

TWO_S_BOOST = {
    'Transform' : {
        'omit' : [],
        'include_only' : ['T']
    },
    'Normal' : {},
    'Boost1_1' : {},
    'Post1_1' : {},
    'Boost1_2' : {
        'omit' : ['S']
    },
    'Boost2_1' : {
        'omit' : ['S']
    },
    'Boost1_3' : {
        'omit' : ['S']
    },
    'Exit1_1' : {
        'omit' : ['W', 'D', 'S'],
    },
    'Exit1_2' : {
        'omit' : ['W', 'D', 'S'],
    },
    'Exit2_1' : {
        'omit' : ['W', 'D', 'S'],
    },
    'Exit1_3' : {
        'omit' : ['W', 'D', 'S'],
    },
    'BuffDummy' : {
        'omit' : [],
        'include_only' : ['B1']
    }
}

REBORN_PZ = {
    'Transform' : {
        'omit' : [],
        'include_only' : ['T']
    },
    'Normal' : {},
    'End' : {
        'omit' : [],
        'include_only' : ['S']
    },
}
# missing:
# thor (screw this guy)
# giovanni (this guy is worse)

C_3MAP = {
    1 : 'C1',
    2 : 'C2',
    3 : 'C3'
}
C1AB_3MAP = {
    1 : 'C1a',
    2 : 'C1b',
    3 : 'C2',
    4 : 'C3'
}
C2AB_3MAP = {
    1 : 'C1',
    2 : 'C2a',
    3 : 'C2b',
    4 : 'C3'
}
C3AB_3MAP = {
    1 : 'C1',
    2 : 'C2',
    3 : 'C3a',
    4 : 'C3b'
}
C4AB_5MAP = {
    1 : 'C1',
    2 : 'C2',
    3 : 'C3',
    4 : 'C4a',
    5 : 'C4b',
    6: 'C5'
}
C3ABC_3MAP = {
    1 : 'C1',
    2 : 'C2',
    3 : 'C3a',
    4 : 'C3b',
    5 : 'C3c'
}
C_5MAP = {
    1 : 'C1',
    2 : 'C2',
    3 : 'C3',
    4 : 'C4',
    5 : 'C5'
}
C2ABC3AB_3MAP = {
    1 : 'C1',
    2 : 'C2a',
    3 : 'C2b',
    4 : 'C2c',
    5 : 'C3a',
    6 : 'C3b'
}
C3AB5AB_5MAP = {
    1 : 'C1',
    2 : 'C2',
    3 : 'C3a',
    4 : 'C3b',
    5 : 'C4',
    6 : 'C5a',
    7 : 'C5b'
}