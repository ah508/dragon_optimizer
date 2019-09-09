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
solverInfo = SolInfo(info)
if config.obj_strat == 'Min Frames':
    subSolverInfo = SubSolInfo(info)

bufferable = False
for element in info.cancels:
    if element != 0:
        bufferable = True
        break

mode = 'Default'
if info.cond != [1, 0] or bufferable:
    mode = 'BnB'
elif info.tCancel:
    mode = 'Transform Cancel'
#note: this breaks jeanne.
if config.bnbOverride:
    mode = 'BnB'

# print('parsed:')
# print(time.process_time() - start_time)

if mode == 'Default':
    skill = LPsolution()
    noskill = LPsolution()
    if config.disp_mode in ['Default', 'Both'] or config.disp_compare:
        skill.solve(info, solverInfo, 1)
        noskill.solve(info, solverInfo, 0)
        if config.obj_strat == 'Min Frames':
            skill.characteristics(objective_only=True)
            noskill.characteristics(objective_only=True)
            skill.solve(info, subSolverInfo, 1, add_const=skill.objective)
            noskill.solve(info, subSolverInfo, 0, add_const=noskill.objective)

    elif config.disp_mode == 'Skill':
        skill.solve(info, solverInfo, 1)
        if config.obj_strat == 'Min Frames':
            skill.characteristics(objective_only=True)
            skill.solve(info, subSolverInfo, 1, add_const=skill.objective)

    elif config.disp_mode == 'No Skill':
        noskill.solve(info, solverInfo, 0)
        if config.obj_strat == 'Min Frames':
            noskill.characteristics(objective_only=True)
            noskill.solve(info, subSolverInfo, 0, add_const=noskill.objective)

    # print('post solve:')
    # print(time.process_time() - start_time)
    skill.characteristics()
    noskill.characteristics()
    
    if skill.solved and noskill.solved:
        zero = rootFind(skill, noskill, info)
    else:
        zero = 'Not Computed'

    final = MainDisplay(skill, noskill, info, zero)


if mode == 'BnB':
    if config.disp_mode == 'No Skill' and not (bufferable or config.bnbOverride or config.disp_compare):
        skill = LPsolution()
        noskill = LPsolution()
        noskill.solve(info, solverInfo, 0)
    
    elif config.disp_mode in ['Skill', 'No Skill'] and config.disp_compare and not (bufferable or config.bnbOverride):
        info.adjacencyGen()
        skill = BnBsolution(info, solverInfo, 1)
        noskill = LPsolution()
        skill.findSolution()
        noskill.solve(info, solverInfo, 0)

    else:
        info.adjacencyGen()
        skill = BnBsolution(info, solverInfo, 1)
        noskill = BnBsolution(info, solverInfo, 0)
        if config.disp_mode in ['Default', 'Both'] or config.disp_compare:
            skill.findSolution()
            noskill.findSolution()
        
        elif config.disp_mode == 'No Skill':
            noskill.findSolution()

        elif config.disp_mode == 'Skill':
            skill.findSolution()
        
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
