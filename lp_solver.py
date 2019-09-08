# import config
# import data_coercion as dc
import numpy as np
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

class LPsolution:
    def __init__(self):
        self.solved = False
        self.type = 'LP'
    
    def solve(self, info, solinfo, skill, **kwargs):
        self.solved = True
        self.info = info
        self.skill = skill
        if 'add_const' in kwargs:
            rhs = robjects.IntVector(solinfo.rhs + solinfo.filler + [1, 0, skill, solinfo.time, kwargs['add_const']])
        else:
            rhs = robjects.IntVector(solinfo.rhs + solinfo.filler + [1, 0, skill, solinfo.time])
        self.result = lpSolve.lp("max", solinfo.obj, solinfo.const, solinfo.dir, rhs, int_vec=solinfo.intreq)
        self.solution = self.result.rx2('solution')
        
    def characteristics(self, **kwargs):
        if self.solved:
            self.objective = np.dot(self.solution, self.info.damage)
            if 'objective_only' not in kwargs:
                self.duration = round((self.info.time + self.info.transformTime + self.skill*self.info.skillTime)/60, 3)
                self.leniency = self.info.time - np.dot(self.solution, self.info.frames)
                self.mps = round(self.objective/self.duration, 3)





# def mainSolver(objective, constraint, direction, rhsMain, rhsFiller, skillAppend, noskillAppend, intreq):    
#     if dc.mode == 'Default':
#         r_rhsSkill = robjects.IntVector(rhsMain + rhsFiller + skillAppend)
#         r_solSkill = lpSolve.lp("max", objective, constraint, direction, r_rhsSkill, int_vec=intreq)
#         skill_solution = r_solSkill.rx2('solution')
#         skill_objective = r_solSkill.rx2('objval')
    
#     if dc.mode == 'Default' or 'BnB':
#         r_rhsNone = robjects.IntVector(rhsMain + rhsFiller + noskillAppend)
#         r_solNone = lpSolve.lp("max", objective, constraint, direction, r_rhsNone, int_vec=intreq)
#         noskill_solution = r_solNone.rx2('solution')
#         noskill_objective = r_solNone.rx2('objval')

#     if dc.mode == 'Default':
#         return skill_solution, noskill_solution, skill_objective, noskill_objective
    
#     if dc.mode == 'BnB':
#         return noskill_solution, noskill_objective
    