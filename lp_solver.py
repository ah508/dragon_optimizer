# import config
# import data_coercion as dc
import numpy as np
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

class LPsolution:
    def __init__(self, info, solInfo, subSolInfo, useSkill):
        self.solved = False
        self.info = info
        self.subSolInfo = subSolInfo
        self.solInfo = solInfo
        self.useSkill = useSkill
        self.type = 'LP'
    
    def solve(self, **kwargs):
        self.solved = True
        if 'add_const' in kwargs:
            rhs = robjects.FloatVector(self.solInfo.rhs + self.solInfo.filler + [1, 0, self.useSkill, self.solInfo.time, kwargs['add_const']])
            method = "min"
            solverInfo = self.subSolInfo
        else:
            rhs = robjects.IntVector(self.solInfo.rhs + self.solInfo.filler + [1, 0, self.useSkill, self.solInfo.time])
            method = "max"
            solverInfo = self.solInfo
        self.result = lpSolve.lp(method, solverInfo.obj, solverInfo.const, solverInfo.dir, rhs, int_vec=solverInfo.intreq)
        self.solution = self.result.rx2('solution')
        
    def characteristics(self, **kwargs):
        if self.solved:
            self.objective = np.dot(self.solution, self.info.damage)
            if 'objective_only' not in kwargs:
                self.duration = round((self.info.time + self.info.transformTime + self.useSkill*self.info.skillTime)/60, 3)
                self.leniency = self.info.time - np.dot(self.solution, self.info.frames)
                self.mps = round(self.objective/self.duration, 3)
