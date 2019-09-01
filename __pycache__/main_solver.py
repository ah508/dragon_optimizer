#import pybnb
import numpy as np
import scipy.optimize as spOpt
from threading import Lock
import copy
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
base = importr('base')
lpSolve = importr('lpSolve')
readr = importr('readr')
lock = Lock()
bestDamage = 0
bestTime = 600
#from dragon_dat import cerberus as dragon


mode = 'Compare Default'
refCombo = ['T  ', 'C1a', 'C1b', 'C2a', 'C2b', 'C3a', 'C3b', 'C4a', 'C4b', 'C5a', 'C5b', 'W  ', 'D  ', 'S  ']

adjacency = None             #dragon.frames
damage = [150, 140, 140, 308, 0, 392, 0, 0, 0, 0, 0, 0, 0, 980]                #dragon.damage
cond = None                  #dragon.skeffect
tMod = 1 + 0                  #dragon.transformation
timeMod = 600*tMod
frameC = [0, 17, 19, 34, 0, 79, 0, 0, 0, 0, 0, 79, 42, 3]                #dragon.frameCount
tTime = 108
sTime = 270
#action = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# frames = [0, 13, 0, 24, 0, 46, 0, 600, 600, 600, 600, 42, 3]

def fZero(x, solSkill, solNone, damage, time, timeADD, skillDur, selection):
    damSkill = (damage[-1]*(x) + (np.dot(solSkill, damage) - damage[-1]))/(time + timeADD + skillDur)
    damNone = np.dot(solNone, damage)/(time + timeADD)
    if selection == 'Zero':
        return damNone - damSkill
    elif selection == 'Compare':
        return damSkill, damNone
    
constraint = ([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # = 1
            0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   # <= 0
            0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,   # <= 0
            0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,   # <= 0
            0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0,   # <= 0
            0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0,   # <= 0
            0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0,   # <= 0
            0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0,   # <= 0
            0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0,   # <= 0
            0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0,   # <= 0
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,    # >= current c1a
            0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,    # >= current c1b
            0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,    # >= current c2a
            0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,    # >= current c2b
            0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,    # >= current c3a
            0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,    # >= current c3b
            0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,    # >= current c4a
            0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,    # >= current c4b
            0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,    # >= current c5a
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,    # >= current c5b
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,    # >= current wait
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,    # >= current dodge
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,    # >= current skill
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1,   # <= 1
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,    # <= 1
            *frameC                                       # <= total time
])

r_obj = robjects.FloatVector(damage)
intreq = robjects.IntVector(range(1, 15))
r_cons = robjects.r['matrix'](constraint, nrow=26, byrow=True)
r_dir = robjects.StrVector(['==', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=',
                            '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '>=', '<=', 
                            '<=', '<='])
if mode == 'Compare Default':
    r_rhsSkill = robjects.IntVector([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, timeMod])
    r_rhsNone = robjects.IntVector([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, timeMod])
    r_solSkill = lpSolve.lp("max", r_obj, r_cons, r_dir, r_rhsSkill, int_vec=intreq).rx2('solution')
    r_solNone = lpSolve.lp("max", r_obj, r_cons, r_dir, r_rhsNone, int_vec=intreq).rx2('solution')
    damSkill, damNone = fZero(1, r_solSkill, r_solNone, damage, timeMod, tTime, sTime, 'Compare')
    print("\n")
    if damSkill >= damNone:
        print("Always Optimal.")
        for i in range(0, len(r_solSkill)):
            if (i < 11 and r_solSkill[i] != 0 and damage[i] != 0) or i >= 11:
                print(f'{refCombo[i]} :  {r_solSkill[i]}')
        print(" ")
        print(f'MOD/s     : {60*damSkill}')
        print(f'Total Mod : {np.dot(r_solSkill, damage)}')
    elif damSkill < damNone:
        print("Skill is a Loss.")
        print("Current Optimum:")
        for i in range(0, len(r_solNone)):
            if (i < 11 and r_solNone[i] != 0 and damage[i] != 0) or i >=11:
                print(f'{refCombo[i]} :  {r_solNone[i]}')
        print(" ")
        print(f'MOD/s     : {60*damNone}')
        print(f'Total Mod : {np.dot(r_solNone, damage)}')
        zero = spOpt.newton(fZero, 1, args=(r_solSkill, r_solNone, damage, timeMod, tTime, sTime, 'Zero'))
        print(f'Skill Coefficient Breakpoint : {zero}')
        print("\n")





# class Simple(pybnb.Problem):
#     def __init__(self):
#         global tMod
#         self._currentNode = 0
#         self._sumDamage = 150
#         self._time = 0
#         self._optString = [0]
#         self._condition = [0, 0]
#         self._endTime = 600*(1 + tMod)
#         self._comboCount = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
       
#     def sense(self):
#         return pybnb.maximize

#     def objective(self):
#         return self._sumDamage

#     def bound(self):
#         global bestDamage
#         global bestTime
#         global r_cons
#         global r_dir
#         global r_obj




        


#         lock.acquire()
#         locBestD = bestDamage
#         locBestT = bestTime
#         lock.release()

#         return (self._sumDamage + ((1+locBestD)/(1+locBestT))*(self._endTime-self._time))

#     def save_state(self, node):
#         node.state = (self._sumDamage, self._time, self._currentNode, self._optString, self._condition, self._comboCount)

#     def load_state(self, node):
#         (self._sumDamage, self._time, self._currentNode, self._optString, self._condition, self._comboCount) = node.state

#     def branch(self):
#         if(self._time > self._endTime):
#             return self.infeasible_objective()

#         global bestDamage
#         global bestTime
#         global adjacency
#         global damage
#         global cond
#         # global frames
#         damages = copy.copy(damage)

#         if (self._condition[1] > 0):
#             for i in range(0, len(damages)-1):
#                 damages[i] = damages[i]*self._condition[0]
        
#         lock.acquire()
#         if(self._sumDamage > bestDamage):
#             bestDamage = self._sumDamage
#             bestTime = self._time
#         lock.release()

#         for nextNode in range(0, len(adjacency)-1):
#             if adjacency[self._currentNode][nextNode] == -1:
#                 continue
#             time = self._time + adjacency[self._currentNode][nextNode]
#             comboCount = self._comboCount
#             comboCount[nextNode + 1] += 1
#             if time > self._endTime:
#                 continue
#             child = pybnb.Node()
#             child.state = (self._sumDamage + damages[nextNode], time, nextNode, 
#                 self._optString + [nextNode], [self._condition[0], self._condition[1] - adjacency[self._currentNode][nextNode]], self._timeTrack + [time], comboCount)
#             yield child

#         if(self._comboCount[-1] < 1 and self._comboCount[1] < 1 and self._time + adjacency[self._currentNode][-1] <= self._endTime):
#             child = pybnb.Node()
#             child.state = (self._sumDamage + damages[12], self._time + 3, 
#             True, 12, self._optString + [12], cond, self._timeTrack + [self._time + 3])
#             yield child

        
#     def notify_solve_begins(self,
#                             comm,
#                             worker_comm,
#                             convergence_checker):
#         pass
#     def notify_new_best_node(self,
#                              node,
#                              current):
#         pass
#     def notify_solve_finished(self,
#                               comm,
#                               worker_comm,
#                               results):
#         pass
    

# problem = Simple()
# solver = pybnb.Solver()
# results = solver.solve(problem,
#                        absolute_gap=0.0001, node_limit=10000000, queue_strategy='bound')
# print(results.best_node.state[4])
# print(results.best_node.state[1])
# print(results.best_node.state[-1])