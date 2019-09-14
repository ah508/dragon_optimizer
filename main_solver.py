# import time
# start_time = time.process_time()

import config
from findZero import rootFind
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import pandas
from data_refine import Refine, SolInfo, SubSolInfo
from bnb_formulation import BnBsolution
import pybnb
from lp_solver import LPsolution
from output import MainDisplay

# complete_dragons = pandas.read_csv('file:dragon_optimizer/discrete_dragon_data.csv', header=0, index_col=0)
complete_dragons = pandas.read_csv('file:discrete_dragon_data.csv', header=0, index_col=0)
dragon = complete_dragons.loc[config.dragon]

info = Refine(dragon)
info.trimmed()
info.speedCheck()
info.addConstraints()
info.adjacencyGen()
solverInfo = SolInfo(info)
# if config.obj_strat == 'Min Frames':
subSolverInfo = SubSolInfo(info)

bufferable = False
for element in info.cancels:
    if element != 0:
        bufferable = True
        break

bnb = (config.bnbOverride or bufferable)

if bnb:
    skill = BnBsolution(info, solverInfo, 1)
    noskill = BnBsolution(info, solverInfo, 0)

elif info.cond != [1, 0]:
    skill = BnBsolution(info, solverInfo, 1)
    noskill = LPsolution(info, solverInfo, subSolverInfo, 0)

else:
    skill = LPsolution(info, solverInfo, subSolverInfo, 1)
    noskill = LPsolution(info, solverInfo, subSolverInfo, 0) 

if config.disp_compare or config.disp_mode in ['Both', 'Default']:
    skill.solve()
    noskill.solve()
    if config.obj_strat == 'Min Frames' and not bnb:
        noskill.characteristics(objective_only=True)
        noskill.solve(add_const=noskill.objective)
        if info.cond == [1, 0]:
            skill.characteristics(objective_only=True)
            skill.solve(add_const=skill.objective)

elif config.disp_mode == 'Skill':
    skill.solve()
    if config.obj_strat == 'Min Frames' and not bnb and info.cond == [1, 0]:
        skill.characteristics(objective_only=True)
        skill.solve(add_const=skill.objective)

elif config.disp_mode == 'No Skill':
    noskill.solve()
    if config.obj_strat == 'Min Frames' and not bnb:
        noskill.characteristics(objective_only=True)
        noskill.solve(add_const=noskill.objective)

skill.characteristics()
noskill.characteristics()

if skill.solved and noskill.solved:
    zero = rootFind(skill, noskill, info)
else:
    zero = 'Not Computed'

final = MainDisplay(skill, noskill, info, zero)
final.output()


# print('++++++++++')
# print(time.process_time() - start_time)
# print('++++++++++')
