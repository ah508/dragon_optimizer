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
            rhs = robjects.FloatVector(solinfo.rhs + solinfo.filler + [1, 0, skill, solinfo.time, kwargs['add_const']])
            method = "min"
        else:
            rhs = robjects.IntVector(solinfo.rhs + solinfo.filler + [1, 0, skill, solinfo.time])
            method = "max"
        self.result = lpSolve.lp(method, solinfo.obj, solinfo.const, solinfo.dir, rhs, int_vec=solinfo.intreq)
        self.solution = self.result.rx2('solution')
        
    def characteristics(self, **kwargs):
        if self.solved:
            self.objective = np.dot(self.solution, self.info.damage)
            if 'objective_only' not in kwargs:
                self.duration = round((self.info.time + self.info.transformTime + self.skill*self.info.skillTime)/60, 3)
                self.leniency = self.info.time - np.dot(self.solution, self.info.frames)
                self.mps = round(self.objective/self.duration, 3)
