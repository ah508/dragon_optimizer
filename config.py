dragon = 'Cerberus'
disp_mode = 'Default' #Default, Skill, No Skill, Transform Cancel, Full List
disp_compare = False
bnbOverride = False
suppress_status = False
leniency = 3
skill_coefficient = 1
attack_rate = 1
haste_coefficient = 1
additional_time = 0 # interpretted as an additive % increase
initial_time = 10 # seconds
obj_strat = 'Default' #'Default', 'Min Frames', 'Dirty'(illegitimate min frames)
                         #NOTE: 'Dirty' is actually surprisingly accurate
integrality = True
bound_method = 'Accurate' #'Accurate', 'None', 'Experimental, Super Experimental'(NOTE:not implemented currently)
queue_strat = 'depth'
include_string = True

# Future Goals:
# finally get around to making the whole darn thing an LP.
# make bnb a legacy option (as a consequence of the above) and implement something separate for complete enum
# be able to compute the pareto boundary for a particular dragon (maximize {damage, -frames})
# implement a dynamic algorithm for the nonconvex cases
# provide some method to graphically display the entire feasible region (through complete enumeration?)