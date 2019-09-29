dragon = 'Cerberus'     # The dragon in question
disp_mode = 'Default'   # Default, or a list with any combination of 
                        # skill, noskill, tcancel
disp_compare = False    # Displays zeros with other solution methods if you override default display
bnbOverride = False     # Forces the solve to use BnB
suppress_status = False # Suppresses output; may not be working properly
leniency = 3            # The number of 'dead frames' between certain actions
skill_coefficient = 1   # Coefficient across all brackets
attack_rate = 1         # Attack speed, assumed to be ceiling for now
rate_method = 'ceil'    # Changes the assumption for attack speed
haste_coefficient = 1   # For those dragons which generate SP
additional_time = 0     # Interpretted as an additive % increase to dragon time
initial_time = 10       # Seconds
obj_strat = 'Default'   # 'Default', 'Min Frames', 'Dirty'(illegitimate min frames)
                        # NOTE: 'Dirty' is actually surprisingly accurate
integrality = True      # Requires integrality constraints
bound_method = 'Accurate' # 'Accurate', 'None'
queue_strat = 'depth'   # The queue strategy for the branch and bound process
include_string = True   # I'm pretty sure this isn't in use at all right now

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