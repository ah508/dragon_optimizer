import config
from functools import lru_cache
import numpy as np
from data_refine import BnBinfo
import pybnb
import copy
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

class BnBsolution(BnBinfo):
    # Handles all information for the purposes of solving the problem by
    # branch and bound.
    # Also used for complete enumeration because... I don't want to
    # write my own method for that yet.
    def __init__(self, dragon, useSkill, transformCancel=False):
        super().__init__(dragon)
        self.adjacencyGen()
        # Generating an adjacency matrix.
        self.useSkill = useSkill
        self.transformCancel = transformCancel
        self.type = 'BnB'
        self.solved = False

    def solve(self):
        self.solved = True
        self.normInfo(bnb=True, skill=self.useSkill)
        # Generating the LP relaxation.
        info = copy.deepcopy(self)
        # This is a relic of a bygone era, when all information was
        # passed as an argument.
        formula = Formulation(info, self.useSkill, self.transformCancel)
        # Formulation could be rewritten to just use inheritence, but
        # it works fine as is.  With inheritence, multiple inheritence
        # would also become a small concern.
        solver = pybnb.Solver()
        self.result = solver.solve(formula, absolute_gap=0.0001, node_limit=10000000, queue_strategy=config.queue_strat)
        self.solution = self.result.best_node.state[-1]
        # Using pybnb to initiate a solve.

    def characteristics(self, tCancel=False):
        if self.solved:
            self.objective = round(self.result.best_node.state[0], 3)
            self.string = self.result.best_node.state[3]
            if tCancel:
                cancel_frames = self.tCancel
            else:
                cancel_frames = 0
            self.duration = round((self.time + self.transformTime + cancel_frames + self.useSkill*self.skillUses*self.skillTime)/60, 3)
            self.leniency = self.time - self.result.best_node.state[1]
            self.mps = round(self.objective/self.duration, 3)
            # Determining the characteristics of the information
            # post-solve.  "objective" is the objective value, and 
            # "duration" is the total time spent in transformation.
            # "leniency" is the number of frames you can lose and still
            # complete the combo.  "mps" is mod per second - total
            # modifer divided by total time.
            # NOTE: "leniency" is a bad variable name - it contradicts
            # the meaning of leniency that is used in config.


@lru_cache(maxsize=2048)
def lp_sol(combo, useSkill, modifier, solInfo):
    cc = copy.copy(combo)
    cc = list(cc)
    del cc[0]
    r_rhs = robjects.IntVector([*solInfo.rhs, *cc, *[1, useSkill*solInfo.skillUses, solInfo.time]])
    r_sol = lpSolve.lp("max", solInfo.altObj, solInfo.constraint, solInfo.dir, r_rhs).rx2('objval')
    return modifier*r_sol[0]
    # This determines the bound on a node for the BnB.

class Formulation(pybnb.Problem):
    # Construction of the branch and bound problem.
    # For more details on this, and the package it comes from, check
    # out the link below:
    # https://pybnb.readthedocs.io/en/stable/getting_started/index.html#defining-a-problem
    def __init__(self, info, useSkill, tCancel):
        self._info = info
        self._useSkill = useSkill
        self._tCancel = tCancel
        self._currentNode = 0
        self._sumDamage = 150
        self._time = 0
        self._optString = [0]
        self._condition = [0, 0]
        self._endTime = info.time
        self._comboCount = (1,) + tuple(np.zeros(info.rlength-1))
        if info.skillUses == 1:
            self._contModif = ((info.cond[0]-1)*info.cond[1]/info.time)+1
        elif info.skillUses >= 2 and config.bound_method != 'None':
            print("this method isn't designed to handle that")
            quit()
        self._skillSP = 30
    
    
    def sense(self):
        return pybnb.maximize

    def objective(self):
        return self._sumDamage

    def bound(self):
        # if config.bound_method == 'Experimental':
        #     bound = lp_sol(self._comboCount, self._useSkill, self._contModif, self._info)
        #     return round(bound, 3)
        if config.bound_method == 'Accurate':
            bound = lp_sol(self._comboCount, self._useSkill, self._contModif, self._info)
            return round(bound, 3)
        elif config.bound_method == 'None':
            return 15000
        # Experimental and Accurate currently do exactly the same job.
        # Experimental is still present as a comment because it is
        # occasionally used for testing purposes.

    def save_state(self, node):
        node.state = (
            self._sumDamage, 
            self._time, 
            self._currentNode, 
            self._optString, 
            self._condition, 
            self._tCancel,
            self._skillSP,
            self._comboCount
            )

    def load_state(self, node):
        (
            self._sumDamage, 
            self._time, 
            self._currentNode, 
            self._optString, 
            self._condition, 
            self._tCancel,
            self._skillSP,
            self._comboCount
            ) = node.state

    def branch(self):
        if(self._time > self._endTime):
            return self.infeasible_objective()

        for nextNode in range(0, len(self._info.adjacency)-1):
            if self._info.adjacency[self._currentNode][nextNode] == -1:
                continue
            if self._tCancel:
                continue
            time = self._time + self._info.adjacency[self._currentNode][nextNode]
            if time > self._endTime:
                continue
            comboCount = self._comboCount[:nextNode] + (self._comboCount[nextNode] + 1,) + self._comboCount[nextNode+1:]
            skill_SP = min(30, self._skillSP + self._info.sp_gen[nextNode])
            condition = [self._condition[0], self._condition[1]-self._info.adjacency[self._currentNode][nextNode]]
            if condition[1] < 0:
                condition = [1, 0]
            damage = self._sumDamage + self._info.damage[nextNode]*condition[0]
            child = pybnb.Node()
            child.state = (damage, time, nextNode, 
                self._optString + [nextNode], condition, self._tCancel, skill_SP, comboCount) 
            yield child

        if(self._comboCount[-1] < self._info.skillUses and self._time + self._info.frames[-1] <= self._endTime and self._useSkill and self._skillSP == 30):
            time = self._time + self._info.frames[-1]
            if self._comboCount[-1] == 0:
                condition = self._info.cond
            else:
                condition = [self._info.cond[0]*(1+self._comboCount[-1]) - self._comboCount[-1], self._info.cond[1]]
            # NOTE: not robust at all^
            # NOTE: actually DANGEROUSLY not robust.  However, as this
            #       is currently only used for a single, highly
            #       specific case, it can stay the time being...
            comboCount = self._comboCount[:-1] +(self._comboCount[-1] + 1,)
            child = pybnb.Node()
            child.state = (self._sumDamage + self._info.damage[self._info.rlength-1], time, 
            self._info.rlength-1, self._optString + [self._info.rlength-1], condition, False, 0, comboCount) 
            yield child
        # The adjacency matrix defines a graph.
        # This method walks that graph to generate nodes for the bnb.
        
    def notify_solve_begins(self,
                            comm,
                            worker_comm,
                            convergence_checker):
        pass
    def notify_new_best_node(self,
                            node,
                            current):
        pass
    def notify_solve_finished(self,
                            comm,
                            worker_comm,
                            results):
        pass
    # these let you know that the solve is still goin'