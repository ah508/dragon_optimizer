import config
from fractions import Fraction
from math import ceil
import numpy as np
import rpy2
import rpy2.robjects as robjects

#####
class Refine:
    def __init__(self, data):
        self.reference = ['T  ', 'C1a', 'C1b', 'C2a', 'C2b', 'C3a', 'C3b', 'C4a', 'C4b', 'C5a', 'C5b', 'W  ', 'D  ', 'S  ']
        self.damage = [150] + [data[9 + 4*i] for i in range(0, 10)] + [0, 0] + [data['Skill Damage']*config.skill_coefficient]
        self.cancels = [0] + [data[11 + 4*i] for i in range(0, 10)] + [0, 0, 0]
        self.cooldown = [0] + [data[12 + 4*i] for i in range(0, 10)] + [0, 0, 0,]
        lastC = [i for i, e in enumerate(self.cooldown) if e != 0]
        self.frames = [0] + [data[10 + 4*i] for i in range(0, 10)] + [self.cooldown[lastC[-1]]] + [data['Dodge Frames']] + [0]
        self.tCancel = data['Transform Cancel']
        self.rlength = 0
        if type(data['Skill Effect']) == str:
            sEffect = float(Fraction(data['Skill Effect']))
        else:
            sEffect = data['Skill Effect']
        self.cond = [sEffect, data['Effect Time']]
        self.transformTime = data['Transformation']
        self.skillTime = data['Skill Duration']
        self.time = config.initial_time*60*(1 + data['DragonTime'] + config.additional_time)
        self.adjacency = []
        

    def trimmed(self):
        delVec = []
        for i in range(1, len(self.damage)-3):
            if [self.damage[i], self.cancels[i], self.cooldown[i], self.frames[i]] == [0, 0, 0, 0]:
                delVec += [i]
        delVec.reverse()
        for vector in [self.damage, self.cancels, self.cooldown, self.frames, self.reference]:
            for indices in delVec:
                del vector[indices]
        self.rlength = len(self.reference)
        self.frames[-1] += config.leniency
        self.frames[-2] += config.leniency
    
    def speedCheck(self):
        if config.attack_rate != 1:
            for i in range(1, self.rlength - 3):
                self.frames[i] = ceil(self.frames[i]/config.attack_rate)
            self.skillTime = ceil(self.skillTime/config.attack_rate)

    def adjacencyGen(self):
        self.adjacency = np.full([self.rlength, self.rlength], -1)
        for i in range(0, self.rlength):
            for j in range(0, self.rlength):
                if i == 0 and j >= self.rlength - 3:
                    if j == self.rlength - 1:
                        self.adjacency[i][j] = self.frames[j] 
                elif i >= self.rlength - 3 and j == 1:
                    self.adjacency[i][j] = self.frames[j] 
                elif i < self.rlength - 3 and j >= self.rlength - 2:
                    self.adjacency[i][j] = self.frames[j] 
                    if j == self.rlength - 2 and self.cancels[i] != 0:
                        self.adjacency[i][j] += self.cancels[i] - config.leniency
                elif i in range(0, self.rlength - 3) and j == i + 1:
                    self.adjacency[i][j] = self.frames[j]
        return self.adjacency
#####


#####
class Constraints:
    def __init__(self, rlength, frames):
        self.rlength = rlength
        self.frames = frames
        self.constraint = [1] + list(np.zeros(rlength - 2))
        self.direction = ['==']
        self.wait = list(np.zeros(rlength))

    def rowGeneration(self):
        self.wait[-3] = 1
        self.wait[-4] = -1
        for cascade in range(1, -4):
            constraint += list(np.zeros(cascade + 1)) + [-1, 1] + list(np.zeros(self.rlength - cascade - 3))
            direction += ['<=']
        constraint += [0]
        for limiters in range(1, self.rlength):
            constraint += list(np.zeros(limiters)) + [1] + list(np.zeros(self.rlength - limiters - 1))
            direction += ['>=']
        constraint += [0, 1] + list(np.zeros(self.rlength - 5)) + [-1, -1, -1]
        constraint += self.wait
        constraint += list(np.zeros(self.rlength - 1)) + [1]
        constraint += self.frames
        direction += ['<=', '<=', '<=', '<=']
#####


#####
class SolInfo:
    def __init__(self, information, constraints):
        self.damage = information.damage
        self.frames = information.frames
        self.rowcount = 2*information.rlength - 1
        self.obj = robjects.FloatVector(self.damage - self.frames)
        self.const = robjects.r['matrix'](constraints.constraint, nrow=self.rowcount, byrow=True)
        self.dir = robjects.StrVector(constraints.direction)
        self.intreq = robjects.IntVector(range(1, len(self.damage)))
        self.rhs = [1] + list(np.zeros(information.rlength - 5))
        self.skillAppend = [1, 0, 1, information.time]
        self.noskillAppend = [1, 0, 0, information.time]
        self.filler = list(np.zeros(information.rlength - 1))
#####
