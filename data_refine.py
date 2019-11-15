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
    """Coerces the data read from the csv to a usable format.

    Parses information from the selected subset of the data. This
    information is common to and necessary for the construction of
    later problems, and is hence intended for inheritence.

    Attributes
    ----------
    reference : [str]
        A reference vector ultimately used for display purposes
    damage : [float]
        Stores damage values for each action. Skill damage is
        adjusted according to config.
    cancels : [float]
        Stores cancel information. Rarely used, but necessary
        for bufferables.
    cooldown : [float]
        Used for determining wait times. May become more useful
        later if more data is collected.
    sp_gen : [float]
        Stores SP generation information. Currently only used
        for one case.
    frames : [float]
        Stores information on the 'cost' (in time) of
        each action.
    t_cancel_f : int
        Represents frames lost when canceling transformation
        with skill. A negative value indicates frames saved.
    skill_num : int
        The maximum number of skill uses allowed. Currently
        useful in only one case.
    transform_time : int
        Time consumed in the transformation animation without
        skill canceling.
    skill_time : float
        Time consumed when using skill. Note: this is not the
        'cost' of using skill.
    cond : [float]
        The effects (or 'condition') resulting from the use
        of skill.
    time : float
        The total available resources (time) with which to act.
        No rounding is done as the behavior is not currently
        known.
    rlength : int
        The 'reference length.' Since this is a value that is
        used frequently in other methods, it is assigned here
        to reduce the need for: len(self.reference)

    Parameters
    ----------
    data : DataFrame
            The "data" for the dragon you intend to optimize.
            Expected to match a specific format (that of the
            imported csv)
    """

    def __init__(self, data):
        self.reference = ['T  ', 'C1a', 'C1b', 'C2a', 'C2b', 'C3a', 'C3b', 'C4a', 'C4b', 'C5a', 'C5b', 'W  ', 'D  ', 'S  ']
        self.damage = [data['Transformation Damage']] + [data[12 + 5*i] for i in range(0, 10)] + [0, 0] + [data['Skill Damage']*config.skill_coefficient]
        self.cancels = [0] + [data[14 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        self.cooldown = [0] + [data[15 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        self.sp_gen = [0] + [data[16 + 5*i] for i in range(0, 10)] + [0, 0, 0]
        lastC = [i for i, e in enumerate(self.cooldown) if e != 0]
        self.frames = [0] + [data[13 + 5*i] for i in range(0, 10)] + [self.cooldown[lastC[-1]]] + [data['Dodge Frames']] + [0]
        self.t_cancel_f = data['Transform Cancel']
        self.skill_num = data['Skill Uses']
        self.transform_time = data['Transformation']
        self.skill_time = data['Skill Duration']
        if type(data['Skill Effect']) == str:
            sEffect = float(Fraction(data['Skill Effect']))
            # Someone somewhere is going to be rather cross with me for
            # using 'type' here, I can feel it in my bones.
        else:
            sEffect = data['Skill Effect']
        sETime = data['Effect Time']
        if config.attack_rate != 1:
            sETime += ceil((data['Effect Timing'] - self.skill_time)/config.attack_rate)
        elif data['Effect Time'] != 0:
            sETime += data['Effect Timing'] - self.skill_time
        # If the effect of skill is a string instead of a number, then
        # it is a fraction (and converted as such).
        # This will need an update if skill handling is changed.
        self.cond = [sEffect, sETime]
        self.time = config.initial_time*60*(1 + data['DragonTime'] + config.additional_time)
        self.trimmed()
        self.rlength = len(self.reference)
        self.haste_check()
        self.speed_check()
        # The data is trimmed and adjusted according to other 
        # properties listed in config. You can go without trimming, but
        # it makes enumerative methods much more intensive.
        

    def trimmed(self):
        """Removes extraneous values from the data."""
        
        delVec = []
        for i in range(1, len(self.damage)-3):
            if [self.damage[i], self.cancels[i], self.cooldown[i], self.frames[i], self.sp_gen[i]] == [0, 0, 0, 0, 0]:
                delVec += [i]
        delVec.reverse()
        for vector in [self.damage, self.cancels, self.cooldown, self.frames, self.reference, self.sp_gen]:
            for indices in delVec:
                del vector[indices]
        # 'empty' columns are found and removed, as they serve no purpose
        self.frames[-1] += config.leniency
        self.frames[-2] += config.leniency
        # Leniency is added as specified in config.
    
    def speed_check(self):
        """Corrects for attack speed, if applicable."""

        if config.attack_rate != 1:
            if config.rate_method == 'ceil':
                for i in range(1, self.rlength - 3):
                    self.frames[i] = ceil(self.frames[i]/config.attack_rate)
                self.skill_time = ceil(self.skill_time/config.attack_rate)
            elif config.rate_method == 'floor':
                for i in range(1, self.rlength - 3):
                    self.frames[i] = floor(self.frames[i]/config.attack_rate)
                self.skill_time = floor(self.skill_time/config.attack_rate)
        # For the time being, the values are conservatively ceil'd.

    def haste_check(self):
        """Corrects for skill haste, if applicable."""

        if config.haste_coefficient != 1:
            for i in range(1, self.rlength - 3):
                self.sp_gen[i] = ceil(self.sp_gen[i]*config.haste_coefficient)
        # ... for those dragons which generate SP 

class LPinfo(Refine):
    """Constructs the information needed for the LPP.

    A subclass of Refine which uses the inherited information to
    construct the objective function, constraint matrix, direction
    vector, righthand side, and integrality constraints. If
    'Min Frames' is specified in config, this also handles adjustment
    of the objective function and addition of a constraint.

    If the solution is determined to need branch and bound, this class
    also handles the construction of the LP relaxation for computation
    of upper bounds. It is not strictly accurate, however, it will
    always overestimate - which is fine.

    This class is intended to be inherited by the appropriate solution
    classes, or by the branch and bound constructor class.

    Attributes
    ----------
    obj : [float(R)]
        An R vector representing the objective function.
    constraint : array
        A numpy array. Automatically converted to an R matrix
        with numpy2ri.
    dir : [string(R)]
        An R vector indicating the 'direction' for each
        constraint.
    rhs : [float(R)]
        An R vector containing the righthand side of the
        constraints.
    intreq : [int(R)]
        An R vector specifying which decision variables are
        required to be integer.
    """
    
    def norm_info(self, bnb=False, skill=1, sub=0, cancel_transform=0):
        """Generates the information needed to solve.
        
        Parameters
        ----------
        bnb : bool(=False)
            Determines whether or not additional constraints are
            generated for a branch and bound process.
        skill : int(=1)
            Determines the number of skill uses permitted for the
            problem. Currently not intended to handle values 
            other than 0 or 1.
        sub : float(=0)
            If a second solve is initiated, this contains the
            optimal value of the previous solve.
        cancel_transform : int(=0)
            Indicates whether or not to cancel transformation
            with skill. May be 0 or 1. Treated as an int rather
            than a bool because it is subtracted from one of the
            rhs values.

        Returns
        -------
        None. This method generates attributes for the class.
        """

        if not sub:
            self.add_constraints(bnb=bnb, skill=skill, cancel_transform=cancel_transform)
            self.altObj = robjects.FloatVector(self.damage)
            if config.obj_strat in ['Default', 'Min Frames']:
                self.obj = self.altObj
            elif config.obj_strat == 'Dirty':
                objective = [i - j for i,j in zip(self.damage, self.frames)]
                self.obj = robjects.FloatVector(objective)
            # Normal construction of the constraints and objective
            # function. Objective function is constructed according to
            # the specification in config.
        else:
            self.obj = robjects.FloatVector(self.frames) # 'objective' to 'self.obj' not sure why this wasn't broken, check to ensure it doesn't break later
            self.constraint.resize((self.rlength+1, self.rlength))
            self.constraint[-1, :] = np.array(self.damage)
            self.direction += ['==']
            self.rhs.resize(self.rlength+1)
            self.rhs[-1] = sub
        self.dir = robjects.StrVector(self.direction)
        self.intreq = robjects.IntVector(range(1, len(self.damage)))
        # As this will eventually be passed to an active R instance,
        # all of the necessary information must be assigned to R 
        # objects.

    def add_constraints(self, bnb=False, skill=1, cancel_transform=0):
        """Constructs the constraint matrix.

        The matrix is constructed to satisfy constraints that are
        interpretable as follows:
        -   You must transform exactly once.
        -   To take any action, you must also take an action that
            immediately precedes it. (For example, you cannot use C2
            three times if you have only used C1 once.)
        -   You must skill up to once, or up to 0 times. (not
            determined by the LP)
        -   Each action takes resources (frames), you cannot take
            actions beyond your resource limit.

        Parameters
        ----------
        bnb : bool(=False)
            Determines whether or not additional constraints are
            generated for a branch and bound process.
        skill : int(=1)
            Determines the number of skill uses permitted for 
            the problem. Currently not intended to handle values
            other than 0 or 1.
        cancel_transform : int(=0)
            Indicates whether or not to cancel transformation
            with skill. May be 0 or 1. Treated as an int rather
            than a bool because it is subtracted from one of the
            rhs values.

        Returns
        -------
        None. This method generates attributes for the class.
        """

        if bnb:
            self.constraint = np.zeros((self.rlength*2 - 1, self.rlength))
            self.rhs = [1] + list(np.zeros(self.rlength-4))
        else:
            self.constraint = np.zeros((self.rlength, self.rlength))
            self.rhs = np.zeros(self.rlength)
            self.rhs[0] = 1
            self.rhs[-3:] = np.array([1-cancel_transform, skill, self.time])
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


class SLPinfo(Refine):
    """Constructs the information needed for the separabe LPP.

    A subclass of Refine which uses the inherited information to
    construct the objective function, constraint matrix, direction
    vector, righthand side, and integrality constraints. If
    'Min Frames' is specified in config, this also handles adjustment
    of the objective function and addition of a constraint.

    Where LPinfo is used for unbuffered convex cases, this class is
    used for unbuffered piecewise convex cases. As there is some small
    interdependence, it may not classify as a 'true' separable linear
    program. However, even if that is the case, the methodology is
    remarkably similar.

    This class is intended to be inherited by the appropriate solution
    classes.

    Attributes
    ----------
    obj : [float(R)]
        An R vector representing the objective function.
    constraint : array
        A numpy array. Automatically converted to an R matrix
        with numpy2ri.
    dir : [string(R)]
        An R vector indicating the 'direction' for each
        constraint.
    rhs : [float(R)]
        An R vector containing the righthand side of the
        constraints.
    intreq : [int(R)]
        An R vector specifying which decision variables are
        required to be integer.
    obj_vec : [float]
        The 'objective vector.' Used to compute the 'real' value
        of the objective function. Generally would not be needed,
        but certain methods use different criteria for the
        objective function.
    time_vec : [int]
        The 'time vector.' Used for reasons similar to obj_vec.
    """

    def sep_info(self, cancel_transform=0, sub=0):
        """Generates the information needed to solve.
        
        Parameters
        ----------
        cancel_transform : int(=0)
            Indicates whether or not to cancel transformation
            with skill. May be 0 or 1. Treated as an int rather
            than a bool because it is subtracted from one of the
            rhs values.
        sub : float(=0)
            If a second solve is initiated, this contains the
            optimal value of the previous solve.
        """

        if not sub:
            self.add_sep_constraints(cancel_transform=cancel_transform)
            self.obj_vec = [0, 0] + self.damage[:-1] + [self.cond[0]*i for i in self.damage[1:-1]] + [self.damage[-1]] + list(np.zeros(self.rlength - 4))
            self.time_vec = [0, 0] + self.frames[:-1] + self.frames[1:] + list(np.zeros(self.rlength - 4))
        else:
            self.constraint.resize(3*self.rlength - 2, 3*self.rlength - 4)
            self.constraint[-1, :2] = np.ones(2)
            self.objective = [0, 0] + self.frames[:-1] + self.frames[1:] + list(np.zeros(self.rlength - 4))
            self.rhs.resize(3*self.rlength - 2)
            self.rhs[-1] = sub
            self.direction += ['==']
        self.obj = robjects.FloatVector(self.objective)
        self.dir = robjects.StrVector(self.direction)
        self.intreq = robjects.IntVector(range(3, self.rlength*3 - 4))      
        # Information assigned to R objects as necessary.

    def add_sep_constraints(self, cancel_transform=0):
        """Constructs the constraint matrix.

        The matrix is constructed to satisfy constraints that are
        interpretable as follows:
        -   You must transform exactly once.
        -   To take any action, you must also take an action that
            immediately precedes it. (For example, you cannot use C2
            three times if you have only used C1 once.)
        -   You must skill up to once, or up to 0 times. (not
            determined by the LP)
        -   Each action takes resources (frames), you cannot take
            actions beyond your resource limit.
        
        Additionally:
        -   Actions taken after using a skill are 'boosted.' Each
            boosted action takes boosted resources in addition to the
            usual resources. You cannot take boosted actions beyond
            these limits.
        -   When exiting the boosted state, you must exit to a valid
            step in the unboosted combo. To ensure that this is
            handled correctly, dummy variables are used to represent
            the step that you exit into.
        -   Boosted and unboosted segments are represented in the
            objective function by separate dummy variables.

        Parameters
        ----------
        bnb : bool(=False)
            Determines whether or not additional constraints are
            generated for a branch and bound process.
        skill : int(=1)
            Determines the number of skill uses permitted for the
            problem. Currently not intended to handle values
            other than 0 or 1.
        cancel_transform : int(=0)
            Indicates whether or not to cancel transformation 
            with skill. May be 0 or 1. Treated as an int rather 
            than a bool because it is subtracted from one of the
            rhs values.
        """

        self.objective = [1, 1] + list(np.zeros(self.rlength*3 - 6))
        self.constraint = np.zeros((3*self.rlength - 3, 3*self.rlength - 4))
        self.constraint[0, 2] = 1
        self.direction = ['==']
        self.rhs = np.zeros(3*self.rlength - 3)
        self.rhs[0] = 1
        self.rhs[-8:-2] = np.array([1-cancel_transform, 0, 1, 1, self.time, self.cond[1] + config.leniency])
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


class BnBinfo(LPinfo):
    """Generates additional information related to branch and bound.

    This is a subclass of LPinfo, which is itself a subclass of Refine.
    This class is intended to be inherited by the branch and bound
    solution class.

    Attributes
    ----------
    adjacency : array
        A numpy array that defines a weighted digraph. Used to 
        determine which actions will be available from a given
        node.
    """

    def adjacencyGen(self):
        """Constructs an adjacency matrix."""

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
