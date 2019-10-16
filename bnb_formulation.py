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
    """Constructs and solves the branch and bound problem.

    BnBsolution is a subclass of BnBinfo, which is a subclass of
    LPinfo, which is a subclass of Refine. It is used to generate the
    information needed for a solution, compute the solution, and
    generate characteristic information about the solution. It also
    handles cases where complete enumeration is necessary, because I
    have yet to write my own methods for that.

    This class is entirely dependent upon pybnb, which you can find at:
    https://github.com/ghackebeil/pybnb

    Attributes
    ----------
    use_skill : int
        Indicates whether or not the use of skill is permitted
        for this problem. Duck typing applies here.
    cancel_transform : bool
        Indicates whether or not to use skill to cancel
        transformation for this problem.
    type : 'BnB'
        A string indicating what 'type' of problem this is.
    solved : bool
        Indicates whether or not this problem was actually
        solved.
    result : class instance
        An instance of the SolverResults class, which contains
        information about the solve.
    solution : [int]
        The 'solution' to the problem. Currently unused.
    objective : float
        The optimal value of the objective function.
    string : [str]
        A vector containing the optimal sequence of actions.
    duration : float
        The duration, in seconds, of the computed combo. This
        is assumed to be fixed, regardless of how many frames
        the combo takes to complete in theory - you cannot 
        prematurely end transformation.
    leniency : int
        The number of frames of total error permitted under
        the initial assumptions. Poorly named, as it clashes
        with the definition used in config.
    mps : float
        'Modifier per second.' Effectively a surrogate 
        measure of DPS - total damage divided by total time.

    Parameters
    ----------
    dragon : DataFrame
        The data for the dragon intended for optimization.
        Should be a subset of a pandas dataframe.
    use_skill : int
        Determines the number of skill uses permitted for the
        problem. Currently not intended to handle values
        other than 0 or 1.
    cancel_transform : bool
        Indicates whether or not to cancel transformation
        with skill.
    """

    def __init__(self, dragon, use_skill, cancel_transform=False):
        super().__init__(dragon)
        self.adjacencyGen()
        # Generating an adjacency matrix.
        self.use_skill = use_skill
        self.cancel_transform = cancel_transform
        self.type = 'BnB'
        self.solved = False

    def solve(self):
        """Constructs and solves the problem.

        Information about the solve is generated, and then used to
        create an instance of Formulation, which is then solved by
        pybnb.
        
        Unfortunately, this is a very messy method. It needs some
        refinement. The information is copied from the class, and then
        passed to Formulation. This is a relic of a bygone time when
        this program passed all of its arguments instead of inheriting
        them.

        Parameters
        ----------
        None. This method uses attributes of the class.

        Returns
        -------
        None. This method generates attributes for the class.
        """

        self.solved = True
        self.norm_info(bnb=True, skill=self.use_skill)
        # Generating the LP relaxation.
        info = copy.deepcopy(self)
        # This is a relic of a bygone era, when all information was
        # passed as an argument.
        formula = Formulation(info, self.use_skill, self.cancel_transform)
        # Formulation could be rewritten to just use inheritence, but
        # it works fine as is.  With inheritence, multiple inheritence
        # would also become a small concern.
        solver = pybnb.Solver()
        self.result = solver.solve(formula, absolute_gap=0.0001, node_limit=10000000, queue_strategy=config.queue_strat)
        self.solution = self.result.best_node.state[-1]
        # Using pybnb to initiate a solve.

    def characteristics(self, cancel_transform=False):
        """Generates characteristic information about the solution.

        Parameters
        ----------
        objective_only : bool(=False)
            If true, indicates that the only desired
            characteristic is the value of the objective function.

        Returns
        -------
        None. This method generates attributes for the class.
        """

        if self.solved:
            self.objective = round(self.result.best_node.state[0], 3)
            self.string = self.result.best_node.state[3]
            if cancel_transform:
                cancel_frames = self.t_cancel_f
            else:
                cancel_frames = 0
            self.duration = round((self.time + self.transform_time + cancel_frames + self.use_skill*self.skill_num*self.skill_time)/60, 3)
            self.leniency = self.time - self.result.best_node.state[1]
            self.mps = round(self.objective/self.duration, 3)
            # Determining the characteristics of the information
            # post-solve.
            # NOTE: "leniency" is a bad variable name - it contradicts
            # the meaning of leniency that is used in config.


@lru_cache(maxsize=2048)
def lp_sol(combo, use_skill, modifier, solInfo):
    """Solves the LP relaxation of the IP problem.

    Uses information about which actions have been taken up to the
    current node to construct an LP relaxation of the IP problem.
    Solving this provides an upper bound on the node which, if worse
    than the objective value of the best explored node, allows us to
    prune the current node and all of its children.

    Parameters
    ----------
    combo : [int]
        A vector indicating how many of each action have been
        taken up to this point in the process.
    use_skill : int
        Indicates whether or not to permit skill for this solve.
    modifier : float
        A rough estimate for the increase afforded by
        the effects of skill. May need future revisions.
    solInfo : class instance
        A copy of the BnBsolution class, with all associated
        attributes.

    Returns
    -------
    float
        The optimal value of the objective function, multiplied
        by a correcting scalar.
    """

    cc = copy.copy(combo)
    cc = list(cc)
    del cc[0]
    r_rhs = robjects.IntVector([*solInfo.rhs, *cc, *[1, use_skill*solInfo.skill_num, solInfo.time]])
    r_sol = lpSolve.lp("max", solInfo.altObj, solInfo.constraint, solInfo.dir, r_rhs).rx2('objval')
    return modifier*r_sol[0]

class Formulation(pybnb.Problem):
    """Constructs a 'formula' for the branch and bound problem.

    Defines the components of the process needed by pybnb to actually
    initiate a solve. Includes methods for loading/saving nodes,
    defining an upper or lower bound, defining the objective function,
    defining the branching process, and a few output methods.
    For more information, you can visit the link below:
    https://pybnb.readthedocs.io/en/stable/getting_started/index.html#defining-a-problem

    This method needs a rehaul/needs to be made obsolete. It is not
    particularly efficient, nor is it easy to understand. On account
    of this, most of the mess will remain messy, since it will all
    get replaced eventually anyways.

    Attributes
    ----------
    _info : class instance
        An instance of BnBsolution, containing all of the
        'information' needed for the process.
    _use_skill : int
        Indicates whether or not to permit the use of skill.
    _cancel_transform : bool
        Indicates whether or not to cancel transformation
        with skill.
    _currentNode : int
        The action associated with the current node. Associated
        with the indices of the adjacency matrix.
    _sumDamage : float
        The sum of damage dealt up to and including the
        current node.
    _time : int
        The total time elapsed since initiating the solve.
    _optString : [int]
        The sequence of actions taken to arrive at the
        current node.
    _condition : [float, int]
        The increase afforded after using skill, and the time
        remaining on that increase.
    _endTime : int
        The total allotted time. The process cannot generate
        nodes exceeding this resource limit.
    _comboCount : [int]
        A list of the number of each action taken to arrive
        at the current node. Needed to compute the bound.
    _contModif : [float]
        An estimate for the average increase afforded by the
        effects of using skill.
    _skillSP : int
        The current SP value for dragon skill.

    Parameters
    ----------
    info : class instance
        An instance of BnBsolution, containing all of the
        'information' needed for the process
    use_skill : int
        Indicates whether or not to permit the use of skill.
    cancel_transform : bool
        Indicates whether or not to cancel transformation
        with skill.
    """

    def __init__(self, info, use_skill, cancel_transform):
        self._info = info
        self._use_skill = use_skill
        self._cancel_transform = cancel_transform
        self._currentNode = 0
        self._sumDamage = 150
        self._time = 0
        self._optString = [0]
        self._condition = [0, 0]
        self._endTime = info.time
        self._comboCount = (1,) + tuple(np.zeros(info.rlength-1))
        if info.skill_num == 1:
            self._contModif = ((info.cond[0]-1)*info.cond[1]/info.time)+1
        elif info.skill_num >= 2 and config.bound_method != 'None':
            print("this method isn't designed to handle that")
            quit()
        self._skillSP = 30
    
    def sense(self):
        return pybnb.maximize

    def objective(self):
        return self._sumDamage

    def bound(self):
        """Calculates the bound on the current node.

        Parameters
        ----------
        None. This method uses attributes of the class.

        Returns
        -------
        float or 150000 (int)
            An upper bound on the node. Or, an arbitrary large
            number that ensures complete enumeration, for cases
            where complete enumeration is needed.
        """
        
        # if config.bound_method == 'Experimental':
        #     bound = lp_sol(self._comboCount, self._use_skill, self._contModif, self._info)
        #     return round(bound, 3)
        if config.bound_method == 'Accurate':
            bound = lp_sol(self._comboCount, self._use_skill, self._contModif, self._info)
            return round(bound, 3)
        elif config.bound_method == 'None':
            return 150000
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
            self._cancel_transform,
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
            self._cancel_transform,
            self._skillSP,
            self._comboCount
            ) = node.state

    def branch(self):
        """Defines the branching process.

        Uses a weighted digraph (the adjacency matrix) to determine
        the set of possible children of the current node. Then,
        assuming that there are sufficient resources, those children
        are generated.

        Parameters
        ----------
        None.
        
        Yields
        ------
        child : class instance
            An instance of Node with a state characterized by 
            these attributes:
                _sumDamage, 
                _time, 
                _currentNode, 
                _optString, 
                _condition, 
                _cancel_transform,
                _skillSP,
                _comboCount
            which are defined by the current node
        """
        if(self._time > self._endTime):
            return self.infeasible_objective()

        for nextNode in range(0, len(self._info.adjacency)-1):
            if self._info.adjacency[self._currentNode][nextNode] == -1:
                continue
            if self._cancel_transform:
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
                self._optString + [nextNode], condition, self._cancel_transform, skill_SP, comboCount) 
            yield child

        if(self._comboCount[-1] < self._info.skill_num and self._time + self._info.frames[-1] <= self._endTime and self._use_skill and self._skillSP == 30):
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