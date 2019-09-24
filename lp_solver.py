import config
import numpy as np
from data_refine import LPinfo, SLPinfo
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

class LPsolution(LPinfo):
    def __init__(self, dragon, useSkill):
        super().__init__(dragon)
        self.solved = False
        self.useSkill = useSkill
        self.type = 'LP'
    
    def solve(self, **kwargs):
        self.solved = True
        if 'add_const' in kwargs:
            self.normInfo(skill=self.useSkill, sub=kwargs['add_const'])
            method = "min"
        else:
            self.normInfo(skill=self.useSkill)
            method = "max"
        rhs = robjects.FloatVector(self.rhs)
        self.result = lpSolve.lp(method, self.obj, self.const, self.dir, rhs, int_vec=self.intreq)
        self.solution = self.result.rx2('solution')
        
    def characteristics(self, objective_only=False, tCancel=False):
        if self.solved:
            if tCancel and not objective_only:
                self.useSkill = 1
                self.solution[-1] = 1.0
                cancel_frames = self.tCancel
            else:
                cancel_frames = 0
            self.objective = np.dot(self.solution, self.damage)
            if not objective_only:
                self.objective = round(self.objective, 3)
                self.duration = round((self.time + self.transformTime + cancel_frames + self.useSkill*self.skillTime)/60, 3)
                self.leniency = self.time - np.dot(self.solution, self.frames)
                if tCancel:
                    self.leniency += config.leniency
                self.mps = round(self.objective/self.duration, 3)

class SLPsolution(SLPinfo):
    def __init__(self, dragon, tcancel):
        super().__init__(dragon)
        self.solved = False
        self.useSkill = True
        self.tcancel = tcancel
        self.type = 'SLP'

    def solve(self, **kwargs):
        self.solved = True
        if 'add_const' in kwargs:
            self.sepInfo(tcancel=self.tcancel, sub=kwargs['add_const'])
            method = "min"
        else:
            self.sepInfo(tcancel=self.tcancel)
            method = "max"
        rhs = robjects.FloatVector(self.rhs)
        self.result = lpSolve.lp(method, self.obj, self.const, self.dir, rhs, int_vec=self.intreq)
        self.solution = self.result.rx2('solution')
    
    def characteristics(self, objective_only=False, tCancel=False):
        if self.solved:
            if tCancel and not objective_only:
                cancel_frames = self.tCancel
            else:
                cancel_frames = 0
            self.objective = np.dot(self.solution, self.objVec)
            if not objective_only:
                self.objective = round(self.objective, 3)
                self.duration = round((self.time + self.transformTime + cancel_frames + self.skillTime)/60, 3)
                self.leniency = self.time - np.dot(self.solution, self.timeVec) 
                if tCancel:
                    self.leniency += config.leniency
                self.mps = round(self.objective/self.duration, 3)


