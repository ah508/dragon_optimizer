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
        self.damage = [150] + [data[10 + 5*i] for i in range(0, 10)] + [0, 0] + [data['Skill Damage']*config.skill_coefficient]
        self.cancels = [0] + [data[12 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        self.cooldown = [0] + [data[13 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        self.sp_gen = [0] + [data[14 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        lastC = [i for i, e in enumerate(self.cooldown) if e != 0]
        self.frames = [0] + [data[11 + 5*i] for i in range(0, 10)] + [self.cooldown[lastC[-1]]] + [data['Dodge Frames']] + [0]
        self.tCancel = data['Transform Cancel']
        self.skillUses = data['Skill Uses']
        self.rlength = 0
        if type(data['Skill Effect']) == str:
            sEffect = float(Fraction(data['Skill Effect']))
        else:
            sEffect = data['Skill Effect']
        self.cond = [sEffect, data['Effect Time']]
        self.transformTime = data['Transformation']
        self.skillTime = data['Skill Duration']
        self.time = config.initial_time*60*(1 + data['DragonTime'] + config.additional_time)
        self.trimmed()
        self.hasteCheck()
        self.speedCheck()
        

    def trimmed(self):
        delVec = []
        for i in range(1, len(self.damage)-3):
            if [self.damage[i], self.cancels[i], self.cooldown[i], self.frames[i], self.sp_gen[i]] == [0, 0, 0, 0, 0]:
                delVec += [i]
        delVec.reverse()
        for vector in [self.damage, self.cancels, self.cooldown, self.frames, self.reference, self.sp_gen]:
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

    def hasteCheck(self):
        if config.haste_coefficient != 1:
            for i in range(1, self.rlength - 3):
                self.sp_gen[i] = ceil(self.sp_gen[i]*config.haste_coefficient)

class LPinfo(Refine):
    def normInfo(self, bnb=False, skill=1, sub=0):
        if not sub:
            self.addConstraints(bnb=bnb, skill=skill)
            self.altObj = robjects.FloatVector(self.damage)
            if config.obj_strat in ['Default', 'Min Frames']:
                self.obj = self.altObj
            elif config.obj_strat == 'Dirty':
                objective = [i - j for i,j in zip(self.damage, self.frames)]
                self.obj = robjects.FloatVector(objective)
        else:
            self.rowcount +=1
            objective = robjects.FloatVector(self.frames)
            self.constraint += self.damage
            self.direction += ['==']
            self.rhs += [sub]
        self.const = robjects.r['matrix'](self.constraint, nrow=self.rowcount, byrow=True)
        self.dir = robjects.StrVector(self.direction)
        self.intreq = robjects.IntVector(range(1, len(self.damage)))

    def addConstraints(self, bnb=False, skill=1):
        self.constraint = [1] + list(np.zeros(self.rlength - 2))
        self.direction = ['==']
        wait = list(np.zeros(self.rlength))
        wait[-3] = 1
        wait[-4] = -1
        for cascade in range(1, self.rlength-4):
            self.constraint += list(np.zeros(cascade + 1)) + [-1, 1] + list(np.zeros(self.rlength - cascade - 3))
            self.direction += ['<=']
        self.constraint += [0]
        if bnb:
            for limiters in range(1, self.rlength):
                self.constraint += list(np.zeros(limiters)) + [1] + list(np.zeros(self.rlength - limiters - 1))
                self.direction += ['>=']
            self.rowcount = 2*self.rlength - 1
            self.rhs = [1] + list(np.zeros(self.rlength - 5))
        else:
            self.rowcount = self.rlength
            self.rhs = [1] + list(np.zeros(self.rlength - 5)) + [1, 0, skill, self.time]
        self.constraint += [0, 1] + list(np.zeros(self.rlength - 5)) + [-1, -1, -1]
        self.constraint += wait
        self.constraint += list(np.zeros(self.rlength - 1)) + [1]
        self.constraint += self.frames
        self.direction += ['<=', '<=', '<=', '<=']


class SLPinfo(Refine):
    def sepInfo(self, tcancel=0, sub=0):
        if not sub:
            self.sepConstraints(tcancel=tcancel)
            self.rowcount = 3*self.rlength - 3
            self.objVec = [0, 0] + self.damage[:-1] + [self.cond[0]*i for i in self.damage[1:-1]] + [self.damage[-1]] + list(np.zeros(self.rlength - 4))
            self.timeVec = [0, 0] + self.frames[:-1] + self.frames[1:] + list(np.zeros(self.rlength - 4))
        else:
            self.constraint += [1, 1] + list(np.zeros(self.rlength*3 - 6))
            self.rowcount += 1
            self.objective = [0, 0] + self.frames[:-1] + self.frames[1:] + list(np.zeros(self.rlength - 4))
            self.rhs += [sub]
            self.direction += ['==']
        self.obj = robjects.FloatVector(self.objective)
        self.const = robjects.r['matrix'](self.constraint, nrow=self.rowcount, byrow=True)
        self.dir = robjects.StrVector(self.direction)
        self.intreq = robjects.IntVector(range(3, self.rlength*3 - 4))      

    def sepConstraints(self, tcancel=0):
        self.objective = [1, 1] + list(np.zeros(self.rlength*3 - 6))
        self.constraint = [0, 0, 1] + list(np.zeros(self.rlength*3 - 7))
        self.direction = ['==']
        self.rhs = [1]
        for cascade in range(0, self.rlength - 4):
            self.constraint += list(np.zeros(cascade + 3)) + [-1, 1] + list(np.zeros(self.rlength - cascade - 4))
            self.constraint += list(np.zeros(self.rlength + cascade - 1)) + [-1] + list(np.zeros(self.rlength - cascade - 5))
            self.direction += ['<=']
            self.rhs += [0]
        for cascade in range(0, self.rlength - 4):
            self.constraint += list(np.zeros(self.rlength + cascade + 1)) + [-1, 1] + list(np.zeros(self.rlength - cascade - 4))
            self.constraint += list(np.zeros(cascade + 1)) + [1] + list(np.zeros(self.rlength - cascade - 5))
            self.direction += ['<=']
            self.rhs += [0]
        for cascade in range(0, self.rlength - 4):
            self.constraint += list(np.zeros(self.rlength + cascade + 1)) + [-1] + list(np.zeros(self.rlength - cascade - 3))
            self.constraint += list(np.zeros(cascade + 1)) + [1] + list(np.zeros(self.rlength - cascade -5))
            self.direction += ['<=']
            self.rhs += [0]
        self.constraint += [0, 0, 0, 1] + list(np.zeros(self.rlength - 5)) + [-1, -1] + list(np.zeros(self.rlength*2 - 5))
        self.constraint += list(np.zeros(self.rlength + 1)) + [1] + list(np.zeros(self.rlength - 5)) + [-1, -1, -1] + list(np.zeros(self.rlength - 4))
        self.constraint += list(np.zeros(2*self.rlength)) + list(np.ones(self.rlength - 4))
        self.constraint += list(np.zeros(2*self.rlength - 1)) + [1] + list(np.zeros(self.rlength - 4))
        self.direction += ['<=', '<=', '==', '<=']
        self.rhs += [1-tcancel, 0, 1, 1]
        self.constraint += [0, 0] + self.frames[:-1] + self.frames[1:] + list(np.zeros(self.rlength - 4))
        self.constraint += list(np.zeros(self.rlength + 1)) + self.frames[1:] + list(np.zeros(self.rlength - 4))
        self.direction += ['<=', '<=']
        self.rhs += [self.time] + [self.cond[1] + config.leniency]
        self.constraint += [1, 0] + [-1*i for i in self.damage[:-1]] + list(np.zeros(2*self.rlength - 5))
        self.constraint += [0, 1] + list(np.zeros(self.rlength - 1)) + [-1*self.cond[0]*i for i in self.damage[1:-1]] + [-1*self.damage[-1]] + list(np.zeros(self.rlength - 4))
        self.direction += ['<=', '<=']
        self.rhs += [0, 0]

class BnBinfo(LPinfo):
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

#####
