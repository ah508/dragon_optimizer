import config
from misc import fZero, dparser, ddisplay
import scipy.optimize as spOpt
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import data_coercion as dc
from bnb_formulation import Formulation
import pybnb
import lp_solver

if dc.mode == 'Default':
    (
        skill_solution, 
        noskill_solution, 
        skill_objective, 
        noskill_objective
     ) = lp_solver.mainSolver(dc.r_obj, dc.r_const, dc.r_dir, dc.rhs, dc.rhsFiller, dc.skillAppend, dc.noskillAppend, dc.intreq)

    skill_damage, noskill_damage = fZero(1, skill_objective, noskill_objective, dc.damage, dc.timeMod, dc.tTime, dc.sTime, 'Compare')

    dparser(skill_damage[0], noskill_damage[0], skill_objective[0], noskill_objective[0], skill_solution, noskill_solution)

if dc.mode == 'BnB':
    optimal_string = None
    skillProblem = Formulation()
    solver = pybnb.Solver()
    bnbSkill = solver.solve(skillProblem,
                        absolute_gap=0.0001, node_limit=10000000, queue_strategy=config.queue_strat)
    skill_obj = bnbSkill.best_node.state[0]
    skill_sol = bnbSkill.best_node.state[-1]
    skill_string = bnbSkill.best_node.state[3]

    if not dc.bufferable and not config.bnbOverride:
        noskill_sol, noskill_obj = lp_solver.mainSolver(dc.r_obj, dc.r_const, dc.r_dir, dc.rhs, dc.rhsFiller, dc.skillAppend, dc.noskillAppend, dc.intreq)
        skill_damage, noskill_damage = fZero(1, skill_obj, noskill_obj, dc.damage, dc.timeMod, dc.tTime, dc.sTime, 'Compare')
        
        if config.include_string:
            dparser(skill_damage, noskill_damage[0], skill_obj, noskill_obj[0], skill_sol, noskill_sol, opt_sk_str=skill_string)
        else:
            dparser(skill_damage, noskill_damage[0], skill_obj, noskill_obj[0], skill_sol, noskill_sol)

    else:
        noskillProblem = Formulation()
        noskillProblem._useSkill = False
        bnbNoskill = solver.solve(noskillProblem, 
                                absolute_gap=0.0001, node_limit=10000000, queue_strategy=config.queue_strat)
        noskill_obj = bnbNoskill.best_node.state[0]
        noskill_sol = bnbNoskill.best_node.state[-1]
        noskill_string = bnbNoskill.best_node.state[3]
        skill_damage, noskill_damage = fZero(1, skill_obj, noskill_obj, dc.damage, dc.timeMod, dc.tTime, dc.sTime, 'Compare')

        if config.include_string:
            dparser(skill_damage, noskill_damage, skill_obj, noskill_obj, skill_sol, noskill_sol, opt_sk_str=skill_string, opt_nosk_str=noskill_string)
        else:
            dparser(skill_damage, noskill_damage, skill_obj, noskill_obj, skill_sol, noskill_sol)