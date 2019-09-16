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
import copy
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
    tcancel = BnBsolution(info, solverInfo, 1, tCancel=True)

elif info.cond != [1, 0]:
    skill = BnBsolution(info, solverInfo, 1)
    noskill = LPsolution(info, solverInfo, subSolverInfo, 0)
    tcancel = BnBsolution(info, solverInfo, 1, tCancel=True)

else:
    skill = LPsolution(info, solverInfo, subSolverInfo, 1)
    noskill = LPsolution(info, solverInfo, subSolverInfo, 0)
    tcancel = LPsolution(info, solverInfo, subSolverInfo, 0) 

if config.disp_compare or config.disp_mode in ['Default', 'Full List']:
    skill.solve()
    noskill.solve()
    tcancel.solve()
    if config.obj_strat == 'Min Frames' and not bnb:
        noskill.characteristics(objective_only=True)
        noskill.solve(add_const=noskill.objective)
        if info.cond == [1, 0]:
            skill.characteristics(objective_only=True)
            skill.solve(add_const=skill.objective)
            tcancel.characteristics(objective_only=True)
            tcancel.solve(add_const=tcancel.objective)

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

elif config.disp_mode == 'Transform Cancel':
    tcancel.solve()
    if config.obj_strat == 'Min Frames' and not bnb and info.cond == [1, 0]:
        tcancel.characteristics(objective_only=True)
        tcancel.solve(add_const=tcancel.objective)

skill.characteristics()
noskill.characteristics()
tcancel.characteristics(tCancel=True)

zero = ['Not Computed', 'Not Computed', 'Not Computed']
if skill.solved and noskill.solved:
    zero[0] = rootFind(skill, noskill, info)
if noskill.solved and tcancel.solved:
    zero[1] = rootFind(tcancel, noskill, info)
if skill.solved and tcancel.solved:
    zero[2] = rootFind(tcancel, skill, info)


final = MainDisplay(skill, noskill, tcancel, info, zero)
final.output()


# print('++++++++++')
# print(time.process_time() - start_time)
# print('++++++++++')
