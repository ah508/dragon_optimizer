import config
import numpy as np
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

class LPsolution:
    def __init__(self, info, useSkill):
        self.solved = False
        self.info = info
        self.useSkill = useSkill
        self.type = 'LP'
    
    def solve(self, **kwargs):
        self.solved = True
        if 'add_const' in kwargs:
            self.info.normInfo(skill=self.useSkill, sub=kwargs['add_const'])
            method = "min"
        else:
            self.info.normInfo(skill=self.useSkill)
            method = "max"
        rhs = robjects.FloatVector(self.info.rhs)
        self.result = lpSolve.lp(method, self.info.obj, self.info.const, self.info.dir, rhs, int_vec=self.info.intreq)
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
                    self.leniency += config.leniency
                self.mps = round(self.objective/self.duration, 3)

class SLPsolution:
    def __init__(self, info, tcancel):
        self.solved = False
        self.info = info
        self.useSkill = True
        self.tcancel = tcancel
        self.type = 'SLP'

    def solve(self, **kwargs):
        self.solved = True
        if 'add_const' in kwargs:
            self.info.sepInfo(tcancel=self.tcancel, sub=kwargs['add_const'])
            method = "min"
        else:
            self.info.sepInfo(tcancel=self.tcancel)
            method = "max"
        rhs = robjects.FloatVector(self.info.rhs)
        self.result = lpSolve.lp(method, self.info.obj, self.info.const, self.info.dir, rhs, int_vec=self.info.intreq)
        self.solution = self.result.rx2('solution')
    
    def characteristics(self, objective_only=False, tCancel=False):
        if self.solved:
            if tCancel and not objective_only:
                cancel_frames = self.info.tCancel
            else:
                cancel_frames = 0
            self.objective = np.dot(self.solution, self.info.objVec)
            if not objective_only:
                self.duration = round((self.info.time + self.info.transformTime + cancel_frames + self.info.skillTime)/60, 3)
                self.leniency = self.info.time - np.dot(self.solution, self.info.timeVec) 
                if tCancel:
                    self.leniency += config.leniency
                self.mps = round(self.objective/self.duration, 3)


