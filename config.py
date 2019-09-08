dragon = 'Cupid'
disp_mode = 'No Skill'
disp_compare = False
bnbOverride = False
leniency = 3
skill_coefficient = 1
attack_rate = 1
additional_time = 0 # interpretted as an additive % increase
initial_time = 10 # seconds
obj_strat = 'Min Frames' #'Default', 'Min Frames', 'Dirty'(illegitimate min frames)
                         #NOTE: 'Dirty' is actually surprisingly accurate
bound_method = 'Experimental' #'Accurate', 'None', 'Experimental, Super Experimental'(NOTE:not implemented currently)
queue_strat = 'depth'
include_string = True

# Future Goals:
# be able to compute the pareto boundary for a particular dragon (maximize {damage, -frames})
# implement a dynamic algorithm for the nonconvex cases
# provide some method to graphically display the entire feasible region (through complete enumeration?)