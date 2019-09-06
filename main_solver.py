import config
# from misc import fZero, dparser, ddisplay
from findZero import rootFind
# import scipy.optimize as spOpt
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import pandas
from data_refine import Refine, SolInfo
from bnb_formulation import BnBsolution
import pybnb
from lp_solver import LPsolution
from output import lpOutput

# complete_dragons = pandas.read_csv('file:dragon_optimizer/discrete_dragon_data.csv', header=0, index_col=0)
complete_dragons = pandas.read_csv('file:C:/Users/Adam/Documents/GACHAAAAA/Optimization/dragon_optimizer/discrete_dragon_data.csv', header=0, index_col=0)
dragon = complete_dragons.loc[config.dragon]

info = Refine(dragon)
info.trimmed()
info.speedCheck()
info.addConstraints()
solverInfo = SolInfo(info)

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


#TODO: set up options for skill only and no skill only[done], reflect those changes in lp_solver[done] and bnb_formulation[done].
#      pare down to reflect the use of new classes.
#      fix lp_solver[done] and bnb_formulation because this breaks them

if mode == 'Default':
    skill = LPsolution()
    noskill = LPsolution()
    if (config.disp_mode == 'Default' or 'Both') or config.disp_compare:
        skill.solve(info, solverInfo, 1)
        noskill.solve(info, solverInfo, 0)

    elif config.disp_mode == 'Skill':
        skill.solve(info, solverInfo, 1)
        # if config.disp_compare:
        #     noskill.solve(solverInfo, 0)

    elif config.disp_mode == 'No Skill':
        noskill.solve(info, solverInfo, 0)
        # if config.disp_compare:
        #     skill.solve(solverInfo, 1)

    skill.characteristics()
    noskill.characteristics()
    
    if skill.solved and noskill.solved:
        zero = round(rootFind(skill, noskill, info), 3)
    else:
        zero = 'Not Computed'

    lpOutput(skill, noskill, info, zero)


if mode == 'BnB':
    if config.disp_mode == 'No Skill' and not (bufferable or config.bnbOverride or config.disp_compare):
        skill = LPsolution()
        noskill = LPsolution()
        noskill.solve(info, solverInfo, 0)
    
    elif (config.disp_mode == 'Skill' or 'No Skill') and config.disp_compare and not (bufferable or config.bnbOverride):
        info.adjacencyGen()
        skill = BnBsolution(info, solverInfo, 1)
        noskill = LPsolution()
        skill.findSolution()
        noskill.solve(info, solverInfo, 0)

    else:
        info.adjacencyGen()
        skill = BnBsolution(info, solverInfo, 1)
        noskill = BnBsolution(info, solverInfo, 0)
        if (config.disp_mode == 'Default' or 'Both') or config.disp_compare:
            skill.findSolution()
            noskill.findSolution()
        
        elif config.disp_mode == 'No Skill':
            noskill.findSolution()

        elif config.disp_mode == 'Skill':
            skill.findSolution()
        
    skill.characteristics()
    noskill.characteristics()

    if skill.solved and noskill.solved:
        zero = round(rootFind(skill, noskill, info), 3)
    else:
        zero = 'Not Computed'

    bnbOutput(skill, noskill, info, zero)


        

        

    





# if mode == 'Default':
#     (
#         skill_solution, 
#         noskill_solution, 
#         skill_objective, 
#         noskill_objective
#      ) = lp_solver.mainSolver(dc.r_obj, dc.r_const, dc.r_dir, dc.rhs, dc.rhsFiller, dc.skillAppend, dc.noskillAppend, dc.intreq)

#     skill_damage, noskill_damage = fZero(1, skill_objective, noskill_objective, dc.damage, dc.timeMod, dc.tTime, dc.sTime, 'Compare')

#     dparser(skill_damage[0], noskill_damage[0], skill_objective[0], noskill_objective[0], skill_solution, noskill_solution)

# if mode == 'BnB':
#     adjacency = info.adjacencyGen()
#     optimal_string = None
#     skillProblem = Formulation()
#     solver = pybnb.Solver()
#     bnbSkill = solver.solve(skillProblem,
#                         absolute_gap=0.0001, node_limit=10000000, queue_strategy=config.queue_strat)
#     skill_obj = bnbSkill.best_node.state[0]
#     skill_sol = bnbSkill.best_node.state[-1]
#     skill_string = bnbSkill.best_node.state[3]

#     if not dc.bufferable and not config.bnbOverride:
#         noskill_sol, noskill_obj = lp_solver.mainSolver(dc.r_obj, dc.r_const, dc.r_dir, dc.rhs, dc.rhsFiller, dc.skillAppend, dc.noskillAppend, dc.intreq)
#         skill_damage, noskill_damage = fZero(1, skill_obj, noskill_obj, dc.damage, dc.timeMod, dc.tTime, dc.sTime, 'Compare')
        
#         if config.include_string:
#             dparser(skill_damage, noskill_damage[0], skill_obj, noskill_obj[0], skill_sol, noskill_sol, opt_sk_str=skill_string)
#         else:
#             dparser(skill_damage, noskill_damage[0], skill_obj, noskill_obj[0], skill_sol, noskill_sol)

#     else:
#         noskillProblem = Formulation()
#         noskillProblem._useSkill = False
#         bnbNoskill = solver.solve(noskillProblem, 
#                                 absolute_gap=0.0001, node_limit=10000000, queue_strategy=config.queue_strat)
#         noskill_obj = bnbNoskill.best_node.state[0]
#         noskill_sol = bnbNoskill.best_node.state[-1]
#         noskill_string = bnbNoskill.best_node.state[3]
#         skill_damage, noskill_damage = fZero(1, skill_obj, noskill_obj, dc.damage, dc.timeMod, dc.tTime, dc.sTime, 'Compare')

#         if config.include_string:
#             dparser(skill_damage, noskill_damage, skill_obj, noskill_obj, skill_sol, noskill_sol, opt_sk_str=skill_string, opt_nosk_str=noskill_string)
#         else:
#             dparser(skill_damage, noskill_damage, skill_obj, noskill_obj, skill_sol, noskill_sol)