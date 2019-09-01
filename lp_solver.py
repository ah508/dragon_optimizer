import config
import data_coercion as dc
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

def mainSolver(objective, constraint, direction, rhsMain, rhsFiller, skillAppend, noskillAppend, intreq):    
    if dc.mode == 'Default':
        r_rhsSkill = robjects.IntVector(rhsMain + rhsFiller + skillAppend)
        r_solSkill = lpSolve.lp("max", objective, constraint, direction, r_rhsSkill, int_vec=intreq)
        skill_solution = r_solSkill.rx2('solution')
        skill_objective = r_solSkill.rx2('objval')
    
    if dc.mode == 'Default' or 'BnB':
        r_rhsNone = robjects.IntVector(rhsMain + rhsFiller + noskillAppend)
        r_solNone = lpSolve.lp("max", objective, constraint, direction, r_rhsNone, int_vec=intreq)
        noskill_solution = r_solNone.rx2('solution')
        noskill_objective = r_solNone.rx2('objval')

    if dc.mode == 'Default':
        return skill_solution, noskill_solution, skill_objective, noskill_objective
    
    if dc.mode == 'BnB':
        return noskill_solution, noskill_objective
    