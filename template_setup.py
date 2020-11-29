import copy
from build_methods import build_tree, Make_Constraints
from template_generators import generate_no_boosts, generate_single_boosts, generate_two_boosts, generate_styx, generate_supmym
from TEMPLATES import *

threehit = build_tree(NO_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S'])
fourhit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 'W', 'D', 'S'])
fivehit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 5, 'W', 'D', 'S'])
sixhit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 5, 6, 'W', 'D', 'S'])
sevenhit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 5, 6, 7, 'W', 'D', 'S'])
styx_tree = build_tree(NO_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S0', 'S1', 'S2', 'S3'])
C3 = Make_Constraints(threehit)
C4_1 = Make_Constraints(fourhit)
C4_2 = Make_Constraints(fourhit)
C4_3 = Make_Constraints(fourhit)
C5 = Make_Constraints(fivehit)
C6_1 = Make_Constraints(sixhit)
C6_2 = Make_Constraints(sixhit)
C7 = Make_Constraints(sevenhit)
styx = Make_Constraints(styx_tree)
sup_mym = Make_Constraints(threehit)
generate_no_boosts(C3, 3, C_3MAP, 'TC3DS1B0')
generate_no_boosts(C4_1, 4, C1AB_3MAP, 'TC1abC3DS1B0')
generate_no_boosts(C4_2, 4, C2AB_3MAP, 'TC2abC3DS1B0')
generate_no_boosts(C4_3, 4, C3AB_3MAP, 'TC3abC3DS1B0')
generate_no_boosts(C5, 5, C_5MAP, 'TC5DS1B0')
generate_no_boosts(C6_1, 6, C2ABC3AB_3MAP, 'TC2abc3abC3DS1B0')
generate_no_boosts(C6_2, 6, C4AB_5MAP, 'TC4abC5DS1B0')
generate_no_boosts(C7, 7, C3AB5AB_5MAP, 'TC3ab5abC5DS1B0')
generate_styx(styx, 3, C_3MAP, 'styx')
generate_supmym(sup_mym, 3, C_3MAP, 'supermym')

threehit1b = build_tree(ONE_S_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S'])
fourhit1b = build_tree(ONE_S_BOOST, include_all=[1, 2, 3, 4, 'W', 'D', 'S'])
C3b = Make_Constraints(threehit1b)
C4b_1 = Make_Constraints(fourhit1b)
C4b_2 = Make_Constraints(fourhit1b)
generate_single_boosts(C3b, 3, C_3MAP, 'TC3DS1B1')
generate_single_boosts(C4b_1, 4, C2AB_3MAP, 'TC2abC3DS1B1')
generate_single_boosts(C4b_2, 4, C3AB_3MAP, 'TC3abC3DS1B1')

threehit2b = build_tree(TWO_S_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S'])
fivehit2b = build_tree(TWO_S_BOOST, include_all=[1, 2, 3, 4, 5, 'W', 'D', 'S'])
C3bb = Make_Constraints(threehit2b)
C5bb = Make_Constraints(fivehit2b)
generate_two_boosts(C3bb, 3, C_3MAP, 'TC3DS2B2')
generate_two_boosts(C5bb, 5, C3ABC_3MAP, 'TC3abcC3DS2B2')