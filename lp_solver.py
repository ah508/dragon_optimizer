import config
import numpy as np
from data_refine import LPinfo, SLPinfo
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

class LPsolution(LPinfo):
    # a subclass of LPinfo for ease of accessing information
    # feeds the LP to a solver (R, lpSolve package)
    def __init__(self, dragon, useSkill, transformCancel=0):
        super().__init__(dragon)
        self.solved = False
        self.useSkill = useSkill
        self.transformCancel = transformCancel
        self.type = 'LP'
    
    def solve(self, **kwargs):
        self.solved = True
        if 'add_const' in kwargs:
            self.normInfo(skill=self.useSkill, tcancel=self.transformCancel, sub=kwargs['add_const'])
            method = "min"
            # used when initiating a second solve to minimize frames
        else:
            self.normInfo(skill=self.useSkill, tcancel=self.transformCancel)
            method = "max"
            # the normal method
            # generates the necessary information with normInfo (see: data_refine)
        rhs = robjects.FloatVector(self.rhs)
        if config.integrality:
            self.result = lpSolve.lp(method, self.obj, self.const, self.dir, rhs, int_vec=self.intreq)
            # the normal method
        else:
            self.result = lpSolve.lp(method, self.obj, self.const, self.dir, rhs)
            # used when integrality constraints are removed
        self.solution = self.result.rx2('solution')
        # retrieving the solution vector from result (an R object)
        
    def characteristics(self, objective_only=False):
        if self.solved:
        # only computed if the problem was actually set up and solved
            if self.transformCancel and not objective_only:
                # self.useSkill = 1
                # self.solution[-1] = 1.0
                cancel_frames = self.tCancel
                # arright, look, I get it
                # using both self.transformCancel and self.tCancel is a terrible sin
                # a terrible, terrible, sin
                # I'll fix it later, I swear
                # when handled by LP, transformation cancelling is handled as if you had not used skill,
                #   and then the damage and frames are applied afterwards
            else:
                cancel_frames = 0
                # if you didn't cancel transformation, there is no change in frames
            self.objective = np.dot(self.solution, self.damage)
            # determining the value of the objective function
            # could also be done with self.objective = self.result.rx2('objval')
            if not objective_only:
                # objective_only is used when you would do a second solve to minimize frames
                # if objective_only isn't true, you can proceed to generate the rest of the information
                self.objective = round(self.objective, 3)
                self.duration = round((self.time + self.transformTime + cancel_frames + self.useSkill*self.skillTime)/60, 3)
                self.leniency = self.time - np.dot(self.solution, self.frames)
                if self.transformCancel:
                    self.leniency += config.leniency
                self.mps = round(self.objective/self.duration, 3)
                # rounding for display purposes
                # objective is the objective value
                # duration is the total time spent in transformation
                # leniency is the number of frames you can lose and still complete the combo
                #   note: bad variable name, contradicts the description of leniency in config
                # mps is mod per second - total modifer divided by total time

class SLPsolution(SLPinfo):
    # second verse, same as the first
    # major difference is using sepInfo to generate all of the constraints
    # otherwise this is nearly identical to LPsolution (save for minor handling differences)
    # maybe they should be consolidated...
    def __init__(self, dragon, tcancel):
        super().__init__(dragon)
        self.solved = False
        self.useSkill = True
        self.transformCancel = tcancel
        self.type = 'SLP'

    def solve(self, **kwargs):
        self.solved = True
        if 'add_const' in kwargs:
            self.sepInfo(tcancel=self.transformCancel, sub=kwargs['add_const'])
            method = "min"
        else:
            self.sepInfo(tcancel=self.transformCancel)
            method = "max"
        rhs = robjects.FloatVector(self.rhs)
        if config.integrality:
            self.result = lpSolve.lp(method, self.obj, self.const, self.dir, rhs, int_vec=self.intreq)
        else:
            self.result = lpSolve.lp(method, self.obj, self.const, self.dir, rhs)
        self.solution = self.result.rx2('solution')
    
    def characteristics(self, objective_only=False):
        if self.solved:
            if self.transformCancel and not objective_only:
                cancel_frames = self.tCancel
            else:
                cancel_frames = 0
            self.objective = np.dot(self.solution, self.objVec)
            if not objective_only:
                self.objective = round(self.objective, 3)
                self.duration = round((self.time + self.transformTime + cancel_frames + self.skillTime)/60, 3)
                self.leniency = self.time - np.dot(self.solution, self.timeVec) 
                if self.transformCancel:
                    self.leniency += config.leniency
                self.mps = round(self.objective/self.duration, 3)