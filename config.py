"""The config file.

Contains settings that are used throughout the rest of the program.

Attributes
----------
dragon : str
    The default dragon.
disp_mode : str or [str]
    The default display mode. May be either 'Default' or a list
    including any combination of 'skill', 'noskill', or 'tcancel'.
    'Default' will solve all problems, and display the maximum
    mod/s from among them. The list will display solutions for
    all methods included in the list.
disp_compare : bool
    Displays the zeros with the other solution methods if the
    default display is overridden.
bnb_override : bool
    Forces the solutions to be branch and bound.
suppress_status : bool
    Unused.
leniency : int
    The number of frames of error permitted on certiain actions.
skill_coefficient : float
    Cumulative value of all modifiers to skill damage.
attack_rate : float
    Attack speed modifier. 1 is normal speed.
rate_method : str
    Changes the assumed behavior for attack speed. May be either
    'floor' or 'ceil'.
haste_coefficient : float
    A modifier for SP gains, when relevant.
additional_time : float
    An additive % increase to transformation time.
initial_time : float
    The initial allotted time, before modifiers.
obj_strat : str
    The strategy used when evaluating combos. May be either
    'Default' 'Min Frames' or 'Dirty'. 'Default' performs no
    additional optimization for time. 'Min Frames' minimizes
    time after maximizing damage. 'Dirty' is like 'Min Frames'
    but worse - though remarkably accurate in most cases.
integrality : bool
    Requires integrality constraints.
dual : bool
    Allows computation of the dual solution.
    NOTE: Not yet implemented.
bound_method : str
    The method of bounding used in the branch and bound process.
    May be either 'Accurate' or 'None'. 'None' amounts to complete
    enumeration.
queue_strat : str
    Specifies the queue strategy for the branch and bound process.
    See pybnb documentation for more.
include_string : bool
    Currently not in use.
"""

dragon = 'Cerberus'
disp_mode = 'Default'
disp_compare = False
bnb_override = False
suppress_status = False
leniency = 3
skill_coefficient = 1
attack_rate = 1
rate_method = 'ceil'
haste_coefficient = 1
additional_time = 0
initial_time = 10
obj_strat = 'Min Frames'
integrality = True
# dual = False
bound_method = 'Accurate'
queue_strat = 'depth'
include_string = True

# Future Goals:
# finally get around to making the whole darn thing an LP. 
#   - sorta done, but not really
# make bnb a legacy option (as a consequence of the above) and implement something separate for complete enum
#   - not entirely feasible at the moment, complete enum is still a todo
# be able to compute the pareto boundary for a particular dragon (maximize {damage, -frames})
#   - not on the menu at the moment, would still be super nice to do
# implement a dynamic algorithm for the nonconvex cases
#   - next on the list
# provide some method to graphically display the entire feasible region (through complete enumeration?)
#   - sorta done, via compute hull (it's not actually the entire feasible region, but it is somewhat analagous)