import config
import data_coercion as dc
from data_coercion import adjacency as adjacency
from functools import lru_cache
import numpy as np
import pybnb
import copy
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

@lru_cache(maxsize=2048)
def lp_sol(combo, useSkill, modifier):
    cc = copy.copy(combo)
    cc = list(cc)
    del cc[0]
    if useSkill:
        r_rhs = robjects.IntVector([*dc.rhs, *cc, *dc.skillAppend])
    else:
        r_rhs = robjects.IntVector([*dc.rhs, *cc, *dc.noskillAppend])
    r_sol = lpSolve.lp("max", dc.r_obj, dc.r_const, dc.r_dir, r_rhs).rx2('objval')
    return modifier*r_sol[0]

class Formulation(pybnb.Problem):
    def __init__(self):
        self._useSkill = True
        self._currentNode = 0
        self._sumDamage = 150
        self._time = 0
        self._optString = [0]
        self._condition = [0, 0]
        self._endTime = dc.timeMod
        self._comboCount = (1,) + tuple(np.zeros(dc.reflength-1))
        self._contModif = ((dc.cond[0]-1)*dc.cond[1]/dc.timeMod)+1
    
    
    def sense(self):
        return pybnb.maximize

    def objective(self):
        return self._sumDamage

    def bound(self):
        if config.bound_method == 'Experimental':
            bound = lp_sol(self._comboCount, self._useSkill, self._contModif)
            return bound
            

        elif config.bound_method == 'Accurate':
            bound = lp_sol(self._comboCount, self._useSkill, self._contModif)
            return bound

        elif config.bound_method == 'None':
            return 15000

        # elif config.bound_method == 'Super Experimental':
        #     if [self._currentNode, self._comboCount[-1]] not in self._dmemo['step']:
        #         self._dmemo['step'] += [[self._currentNode, self._comboCount[-1]]]
        #         self._dmemo['damage'] += [self._sumDamage]
        #         self._dmemo['time'] += [self._time]
        #         return 10000000000
        #     else:
        #         index = self._dmemo['step'].index([self._currentNode, self._comboCount[-1]])
        #         if self._sumDamage <= self._dmemo['damage'][index] and self._time >= self._dmemo['time'][index]:
        #             return self.infeasible_objective()
        #         else:
        #             self._dmemo['damage'][index] = self._sumDamage
        #             self._dmemo['time'][index] = self._time
        #             return 10000000000


    def save_state(self, node):
        node.state = (
            self._sumDamage, 
            self._time, 
            self._currentNode, 
            self._optString, 
            self._condition, 
            self._comboCount
            )

    def load_state(self, node):
        (
            self._sumDamage, 
            self._time, 
            self._currentNode, 
            self._optString, 
            self._condition, 
            self._comboCount
            ) = node.state

    def branch(self):
        if(self._time > self._endTime):
            return self.infeasible_objective()
        
        damages = copy.copy(dc.damage)

        if (self._condition[1] > 0):
            for i in range(0, len(damages)-1):
                damages[i] = damages[i]*self._condition[0]

        for nextNode in range(0, len(adjacency)-1):
            if adjacency[self._currentNode][nextNode] == -1:
                continue
            time = self._time + adjacency[self._currentNode][nextNode]
            comboCount = self._comboCount[:nextNode] + (self._comboCount[nextNode] + 1,) + self._comboCount[nextNode+1:]
            if time > self._endTime:
                continue
            child = pybnb.Node()
            child.state = (self._sumDamage + damages[nextNode], time, nextNode, 
                self._optString + [nextNode], [self._condition[0], self._condition[1] - adjacency[self._currentNode][nextNode]], comboCount)
            yield child

        if(self._comboCount[-1] < 1 and self._time + dc.frameC[-1] <= self._endTime and self._useSkill):
            time = self._time + dc.frameC[-1]
            comboCount = self._comboCount[:-1] +(1,)
            child = pybnb.Node()
            child.state = (self._sumDamage + damages[dc.reflength-1], time, 
            dc.reflength-1, self._optString + [dc.reflength-1], dc.cond, comboCount)
            yield child

        
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