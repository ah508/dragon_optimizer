import copy
from build_methods import build_tree, Make_Constraints
from template_generators import *
from TEMPLATES import *

threehit = build_tree(NO_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S'])
fourhit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 'W', 'D', 'S'])
fivehit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 5, 'W', 'D', 'S'])
sixhit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 5, 6, 'W', 'D', 'S'])
sevenhit = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 5, 6, 7, 'W', 'D', 'S'])
styx_tree = build_tree(NO_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S0', 'S1', 'S2', 'S3'])
hbh_tree = build_tree(NO_BOOST, include_all=[1, 2, 3, 4, 'D_Sa', 'D_Ea', 'D_Sb', 'D_Eb', 'W', 'D', 'S'])
rpos_tree = build_tree(REBORN_POS, include_all=[1, 2, 3, 'W', 'D', 'S'])
threehitdelay = build_tree(NO_BOOST, include_all=[1, 2, 3, 'DUMMY_S', 'DUMMY_E', 'W', 'D', 'S'])

C3 = Make_Constraints(threehit)
C4_1 = Make_Constraints(fourhit)
C4_2 = Make_Constraints(fourhit)
C4_3 = Make_Constraints(fourhit)
C5 = Make_Constraints(fivehit)
C6_1 = Make_Constraints(sixhit)
C6_2 = Make_Constraints(sixhit)
C7 = Make_Constraints(sevenhit)
sup_mym = Make_Constraints(threehit)
styx = Make_Constraints(styx_tree)
hbh = Make_Constraints(hbh_tree)
reborn_pos = Make_Constraints(rpos_tree)
C3_delay = Make_Constraints(threehitdelay)

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
generate_hbh(hbh, 4, C3AB_3MAP, 'hbh')
generate_reborn_pos(reborn_pos, 3, C_3MAP, 'reborn_pos')
generate_c3_delay(C3_delay, 3, C_3MAP, 'C3DELAY')

threehit1b = build_tree(ONE_S_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S'])
fourhit1b = build_tree(ONE_S_BOOST, include_all=[1, 2, 3, 4, 'W', 'D', 'S'])
levi_tree = build_tree(ONE_S_BOOST, include_all=[1, 2, 3, 'DUMMY_S', 'DUMMY_E', 'W', 'D', 'S'])

C3b = Make_Constraints(threehit1b)
C4b_1 = Make_Constraints(fourhit1b)
C4b_2 = Make_Constraints(fourhit1b)
leviathan = Make_Constraints(levi_tree)

generate_single_boosts(C3b, 3, C_3MAP, 'TC3DS1B1')
generate_single_boosts(C4b_1, 4, C2AB_3MAP, 'TC2abC3DS1B1')
generate_single_boosts(C4b_2, 4, C3AB_3MAP, 'TC3abC3DS1B1')
generate_leviathan(leviathan, 3, C_3MAP, 'leviathan')

threehit2b = build_tree(TWO_S_BOOST, include_all=[1, 2, 3, 'W', 'D', 'S'])
fivehit2b = build_tree(TWO_S_BOOST, include_all=[1, 2, 3, 4, 5, 'W', 'D', 'S'])

C3bb = Make_Constraints(threehit2b)
C5bb = Make_Constraints(fivehit2b)

generate_two_boosts(C3bb, 3, C_3MAP, 'TC3DS2B2')
generate_two_boosts(C5bb, 5, C3ABC_3MAP, 'TC3abcC3DS2B2')