import config
from fractions import Fraction
from math import ceil, floor #floor is currently not needed
import numpy as np
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.numpy2ri import numpy2ri
robjects.numpy2ri.activate()

#####
class Refine:
    # Refine takes the data read from the csv and coerces it to a usable format
    def __init__(self, data):
        self.reference = ['T  ', 'C1a', 'C1b', 'C2a', 'C2b', 'C3a', 'C3b', 'C4a', 'C4b', 'C5a', 'C5b', 'W  ', 'D  ', 'S  ']
        # a reference vector ultimately used for display purposes
        self.damage = [150] + [data[11 + 5*i] for i in range(0, 10)] + [0, 0] + [data['Skill Damage']*config.skill_coefficient]
        # stores damage values for each action - skill damage is adjusted according to config
        self.cancels = [0] + [data[13 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        # stores cancel information - rarely used, but vital for 'bufferable' cases
        self.cooldown = [0] + [data[14 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        # this may become more relevant later on, but for the time being it's mostly used to determine wait values
        self.sp_gen = [0] + [data[15 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        # stores SP generation information - currently only used for psiren
        lastC = [i for i, e in enumerate(self.cooldown) if e != 0]
        self.frames = [0] + [data[12 + 5*i] for i in range(0, 10)] + [self.cooldown[lastC[-1]]] + [data['Dodge Frames']] + [0]
        # indices for nonzero cooldown values are determined (c3 or c5, generally)
        # a vector for frames is constructed from usual framedata, and the last nonzero cooldown value
        self.tCancel = data['Transform Cancel']
        # 'frames lost when canceling transformation with skill' - a negative value indicates frames saved
        self.skillUses = data['Skill Uses']
        # for dragons with multiple uses of skill (curse you psiren!)
        self.rlength = 0
        # a filler value for reference length, properly assigned later
        self.transformTime = data['Transformation']
        # time consumed in the transformation animation (without canceling)
        self.skillTime = data['Skill Duration']
        # frames necessary to cast skill
        if type(data['Skill Effect']) == str:
            sEffect = float(Fraction(data['Skill Effect']))
            # someone somewhere is gonna bag me for using type here, I can feel it in my bones
        else:
            sEffect = data['Skill Effect']
        sETime = data['Effect Time']
        if config.attack_rate != 1:
            sETime += ceil((data['Effect Timing'] - self.skillTime)/config.attack_rate)
        elif data['Effect Time'] != 0:
            sETime += data['Effect Timing'] - self.skillTime
        # if the effect of skill is a string instead of a number, then it is a fraction (and converted as such)
        # if we ever update to more accurate skill handling, this will need an update
        self.cond = [sEffect, sETime]
        # duration of skill effects
        self.time = config.initial_time*60*(1 + data['DragonTime'] + config.additional_time)
        # total available frames in which to act
        self.trimmed()
        self.hasteCheck()
        self.speedCheck()
        # the data is trimmed and adjusted according to other properties listed in config
        # you can go without trimming, but it makes enumerative methods much more intensive
        

    def trimmed(self):
        delVec = []
        for i in range(1, len(self.damage)-3):
            if [self.damage[i], self.cancels[i], self.cooldown[i], self.frames[i], self.sp_gen[i]] == [0, 0, 0, 0, 0]:
                delVec += [i]
        delVec.reverse()
        for vector in [self.damage, self.cancels, self.cooldown, self.frames, self.reference, self.sp_gen]:
            for indices in delVec:
                del vector[indices]
        # 'empty' columns are found and removed, as they serve no purpose
        self.rlength = len(self.reference) # the reference length is properly assigned
        self.frames[-1] += config.leniency
        self.frames[-2] += config.leniency
        # leniency is added as specified in config
    
    def speedCheck(self):
        if config.attack_rate != 1:
            if config.rate_method == 'ceil':
                for i in range(1, self.rlength - 3):
                    self.frames[i] = ceil(self.frames[i]/config.attack_rate)
                self.skillTime = ceil(self.skillTime/config.attack_rate)
            elif config.rate_method == 'floor':
                for i in range(1, self.rlength - 3):
                    self.frames[i] = floor(self.frames[i]/config.attack_rate)
                self.skillTime = floor(self.skillTime/config.attack_rate)
        # attack speed handling, as specified in config
        # for the time being, the values are conservatively ceil'd

    def hasteCheck(self):
        if config.haste_coefficient != 1:
            for i in range(1, self.rlength - 3):
                self.sp_gen[i] = ceil(self.sp_gen[i]*config.haste_coefficient)
        # ... for those dragons which generate SP 

class LPinfo(Refine):
    # a subclass of Refine that constructs the info needed for the LPP
    # also used to construct the LP relaxation used as a bound in BnB - see BnBinfo/bnb_formulation
    def normInfo(self, bnb=False, skill=1, sub=0, tcancel=0):
        if not sub:
            self.addConstraints(bnb=bnb, skill=skill, tcancel=tcancel)
            self.altObj = robjects.FloatVector(self.damage)
            if config.obj_strat in ['Default', 'Min Frames']:
                self.obj = self.altObj
            elif config.obj_strat == 'Dirty':
                objective = [i - j for i,j in zip(self.damage, self.frames)]
                self.obj = robjects.FloatVector(objective)
            # normal construction of the constraints and objective function
            # objective function is constructed according to the specification in config
        else:
            objective = robjects.FloatVector(self.frames)
            self.constraint.resize((self.rlength+1, self.rlength))
            self.constraint[-1, :] = np.array(self.damage)
            self.direction += ['==']
            self.rhs.resize(self.rlength+1)
            self.rhs[-1] = sub
            # sub denotes a second solve to minimize frames
            # as such, an additional constraint is added and the objective function is changed
        # self.const = self.constraint
        # print(self.constraint)
        # print(self.rhs)
        self.dir = robjects.StrVector(self.direction)
        self.intreq = robjects.IntVector(range(1, len(self.damage)))
        # as this will eventually be passed to an active R instance, all of the necessary 
        #   information must be assigned to R objects

    def addConstraints(self, bnb=False, skill=1, tcancel=0):
        if bnb:
            self.constraint = np.zeros((self.rlength*2 - 1, self.rlength))
            self.rhs = [1] + list(np.zeros(self.rlength-4))
        else:
            self.constraint = np.zeros((self.rlength, self.rlength))
            self.rhs = np.zeros(self.rlength)
            self.rhs[0] = 1
            self.rhs[-3:] = np.array([1-tcancel, skill, self.time])
        self.constraint[0, 0] = 1
        self.direction = ['==']
        for cascade in range(1, self.rlength - 3):
            self.constraint[cascade, cascade] = -1
            self.constraint[cascade, cascade+1] = 1
            self.direction += ['<=']
        if bnb:
            for limiters in range(0, self.rlength - 1):
                self.constraint[self.rlength + limiters - 3, limiters + 1] = 1
                self.direction += ['>=']
        self.constraint[-3, 1] = 1
        self.constraint[-3, -3:] = -1*np.ones(3)
        self.constraint[-2, -1] = 1
        self.constraint[-1, :] = np.array(self.frames)
        self.direction += ['<=', '<=', '<=']
        # This method handles the construction of constraints for a particular dragon (or problem)
        # It is a rather messy affair.
        # To explain as simply as possible:
        #   Since the constraints will (usually) follow a particular pattern, if we have sufficient
        #   information (determined during initialization) we can construct them on the fly. This 
        #   particular construction results in a very long, silly looking vector that we can turn
        #   into a matrix because we know how many rows the constraint matrix for this problem will
        #   have.
        # The essential requirements are:
        #   You must transform once, and only once.
        #   To take any action, you must also take an action that immediately precedes it.
        #       - for example, you cannot use C2 three times if you have only used C1 once.
        #   You must skill exactly once, or exactly 0 times. (not determined by the LP)
        #   Each action takes resources (frames), you cannot take actions beyond your resource limit.
        # 
        # the rhs and direction vectors are constructed accordingly.
        # (I'm sorry if this all sounds a little vague, if you have any questions about it feel free
        #  to ask me directly)



class SLPinfo(Refine):
    # similar to LPinfo, except for separable linear programs
    # due to that resemblence, I'm not going to comment this as thoroughly
    def sepInfo(self, tcancel=0, sub=0):
        if not sub:
            self.sepConstraints(tcancel=tcancel)
            self.objVec = [0, 0] + self.damage[:-1] + [self.cond[0]*i for i in self.damage[1:-1]] + [self.damage[-1]] + list(np.zeros(self.rlength - 4))
            self.timeVec = [0, 0] + self.frames[:-1] + self.frames[1:] + list(np.zeros(self.rlength - 4))
        else:
            self.constraint.resize(3*self.rlength - 2, 3*self.rlength - 4)
            self.constraint[-1, :2] = np.ones(2)
            self.objective = [0, 0] + self.frames[:-1] + self.frames[1:] + list(np.zeros(self.rlength - 4))
            self.rhs.resize(3*self.rlength - 2)
            self.rhs[-1] = sub
            self.direction += ['==']
            # sub denotes a second solve to minimize frames
        self.obj = robjects.FloatVector(self.objective)
        self.dir = robjects.StrVector(self.direction)
        self.intreq = robjects.IntVector(range(3, self.rlength*3 - 4))      
        # information assigned to R objects as necessary

    def sepConstraints(self, tcancel=0):
        self.objective = [1, 1] + list(np.zeros(self.rlength*3 - 6))
        self.constraint = np.zeros((3*self.rlength - 3, 3*self.rlength - 4))
        self.constraint[0, 2] = 1
        self.direction = ['==']
        self.rhs = np.zeros(3*self.rlength - 3)
        self.rhs[0] = 1
        self.rhs[-8:-2] = np.array([1-tcancel, 0, 1, 1, self.time, self.cond[1] + config.leniency])
        for cascade in range(1, self.rlength - 3):
            self.constraint[cascade, cascade + 2:cascade + 4] = np.array([-1, 1])
            self.constraint[cascade, 3 - self.rlength + cascade] = -1
            self.direction += ['<=']
        for cascade in range(self.rlength - 3, 2*self.rlength - 7):
            self.constraint[cascade, cascade + 4:cascade + 6] = np.array([-1, 1])
            self.constraint[cascade, 7 - 2*self.rlength + cascade] = 1
            self.direction += ['<=']
        for cascade in range(2*self.rlength - 7, 3*self.rlength - 11):
            self.constraint[cascade, cascade] = -1
            self.constraint[cascade, 11 - 3*self.rlength + cascade] = 1
            self.direction += ['<=']
        self.constraint[-8, 3] = 1
        self.constraint[-8, self.rlength - 1:self.rlength + 1] = -1*np.ones(2)
        self.constraint[-7, self.rlength + 1] = 1
        self.constraint[-7, 1 - self.rlength:4 - self.rlength] = -1*np.ones(3)
        self.constraint[-6, 4 - self.rlength:] = np.ones(self.rlength-4)
        self.constraint[-5, 3 - self.rlength] = 1
        self.constraint[-4, 2:4 - self.rlength] = np.array(self.frames[:-1] + self.frames[1:])
        self.constraint[-3, self.rlength + 1:4 - self.rlength] = np.array(self.frames[1:])
        self.constraint[-2, 0] = 1
        self.constraint[-2, 2:self.rlength + 1] = np.array([-1*i for i in self.damage[:-1]])
        self.constraint[-1, 1] = 1
        self.constraint[-1, self.rlength + 1:4 - self.rlength] = np.array([-1*self.cond[0]*i for i in self.damage[1:-1]] + [-1*self.damage[-1]])
        self.direction += ['<=', '<=', '==', '<=', '<=', '<=', '<=', '<=']
        # second verse, same as the first... just a bit more complex this time
        # as this is separable linear programming (or at least, the principles used in the formulation of
        # this problem draw heavily from those that direct separable linear programming), I don't believe
        # that I can offer as simple of an explanation of what they achieve.
        # -- may add to this later with proper justifications --

class BnBinfo(LPinfo):
    # a subclass of LPinfo used to construct an adjacency matrix for the branch and bound process
    # naturally permits the generation of constraints and the like that LPinfo does
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
                    if j == self.rlength - 3 and self.cancels[i] != 0:
                        self.adjacency[i][j] += self.cancels[i]

#####
