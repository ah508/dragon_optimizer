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
        
    def characteristics(self, objective_only=False, tCancel=False):
        if self.solved:
            if tCancel and not objective_only:
                self.useSkill = 1
                self.solution[-1] = 1.0
                cancel_frames = self.info.tCancel
            else:
                cancel_frames = 0
            self.objective = np.dot(self.solution, self.info.damage)
            if not objective_only:
                self.duration = round((self.info.time + self.info.transformTime + cancel_frames + self.useSkill*self.info.skillTime)/60, 3)
                self.leniency = self.info.time - np.dot(self.solution, self.info.frames)
                if tCancel:
                    self.leniency += 3
                self.mps = round(self.objective/self.duration, 3)
        # else:
        #     self.mps = 0
