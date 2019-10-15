import config
import numpy as np
from data_refine import LPinfo, SLPinfo
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
lpSolve = importr('lpSolve')

class LPsolution(LPinfo):
    """Constructs and solves the linear programming problem.

    LPsolution is a subclass of LPinfo, which is in turn a subclass of
    Refine. It is used to construct the information needed to generate
    a solution, compute the solution, potentially generate a different
    solution under different conditions, and generate characteristic
    information defining the solution.

    Attributes
    ----------
    solved : bool
        Indicates whether or not this problem was actually
        solved.
    useSkill : int
        Indicates the number of skill uses permitted for this
        problem.
    transformCancel : int
        Indicates whether or not to use skill to cancel
        transformation for this problem.
    type : 'LP'
        A string indicating what 'type' of problem this is.
    result : (R object)
        An lp object generated by the R package lpSolve.
        Contains the information used in and produced by the
        actual solution process.
    solution : [int(R)] or [float(R)]
        A vector containing the optimal values of the
        decision variables.
    objective : float
        The optimal value of the desired objective function.
        It is not obtained directly from the solver results,
        because a different objective function is used when
        initiating a second solve. The two objectives are not
        solved for simultaneously because to my knowledge
        lpSolve does not tackle pareto optimality.
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
    useSkill : int
        Determines the number of skill uses permitted for the
        problem. Currently not intended to handle values
        other than 0 or 1.
    transformCancel : int(=0)
        Indicates whether or not to cancel transformation
        with skill. May be 0 or 1. Treated as an int rather
        than a bool because of how it is used in other methods.
    """

    def __init__(self, dragon, useSkill, transformCancel=0):
        super().__init__(dragon)
        self.solved = False
        self.useSkill = useSkill
        self.transformCancel = transformCancel
        self.type = 'LP'
    
    def solve(self, **kwargs):
        """Constructs and solves the problem.

        Parameters
        ----------
        **kwargs
            add_const : float
                Adds an equality constraint. Used only when
                initiating a second solve. Should be the optimal
                value of the objective function of the first solve.
        
        Returns
        -------
        None. This method generates attributes for the class.
        """

        self.solved = True
        if 'add_const' in kwargs:
            self.normInfo(skill=self.useSkill, tcancel=self.transformCancel, sub=kwargs['add_const'])
            method = "min"
            # used when initiating a second solve to minimize frames
        else:
            self.normInfo(skill=self.useSkill, tcancel=self.transformCancel)
            method = "max"
        if config.integrality:
            self.result = lpSolve.lp(method, self.obj, self.constraint, self.dir, self.rhs, int_vec=self.intreq)
        else:
            self.result = lpSolve.lp(method, self.obj, self.constraint, self.dir, self.rhs)
            # used when integrality constraints are removed
        self.solution = self.result.rx2('solution')
        
    def characteristics(self, objective_only=False):
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
        # only computed if the problem was actually set up and solved
            if self.transformCancel and not objective_only:
                cancel_frames = self.tCancel
            else:
                cancel_frames = 0
                # If you didn't cancel transformation, there is no
                # change in frames.
            self.objective = np.dot(self.solution, self.damage)
            # Determining the value of the objective function.
            # Could also be done with:
            # self.objective = self.result.rx2('objval')
            if not objective_only:
                # objective_only is used when you would do a second
                # solve to minimize frames.
                self.objective = round(self.objective, 3)
                self.duration = round((self.time + self.transformTime + cancel_frames + self.useSkill*self.skillTime)/60, 3)
                self.leniency = self.time - np.dot(self.solution, self.frames)
                if self.transformCancel:
                    self.leniency += config.leniency
                self.mps = round(self.objective/self.duration, 3)
                # rounding for display purposes
                # note: leniency is a bad variable name

class SLPsolution(SLPinfo):
    """Constructs and solves the separable linear programming problem.

    SLPsolution is a subclass of SLPinfo, and hence a subclass of
    Refine. It is used to construct the information needed to generate
    a solution, compute the solution, potentially generate a different
    solution under different conditions, and generate characteristic
    information defining the solution.

    This class is very similar to LPsolution, and in the future they
    may be consolidated.

    Attributes
    ----------
    solved : bool
        Indicates whether or not this problem was actually
        solved.
    useSkill : int
        Indicates the number of skill uses permitted for this
        problem. Skills are used by default when solving with
        this method - not using skill should always result in
        a standard LPP. This attribute exists because it some
        methods need it to exist.
    transformCancel : int
        Indicates whether or not to use skill to cancel
        transformation for this problem.
    type : 'LP'
        A string indicating what 'type' of problem this is.
    result : (R object)
        An lp object generated by the R package lpSolve.
        Contains the information used in and produced by the
        actual solution process.
    solution : [int(R)] or [float(R)]
        A vector containing the optimal values of the
        decision variables.
    objective : float
        The optimal value of the desired objective function.
        It is not obtained directly from the solver results,
        because a different objective function is used when
        initiating a second solve. The two objectives are not
        solved for simultaneously because to my knowledge
        lpSolve does not tackle pareto optimality.
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
    tcancel : int
        Indicates whether or not to cancel transformation
        with skill. May be 0 or 1. Treated as an int rather
        than a bool because of how it is used in other methods.
    """

    def __init__(self, dragon, tcancel):
        super().__init__(dragon)
        self.solved = False
        self.useSkill = True
        self.transformCancel = tcancel
        self.type = 'SLP'

    def solve(self, **kwargs):
        """Constructs and solves the problem.

        Parameters
        ----------
        **kwargs
            add_const : float
                Adds an equality constraint. Used only when
                initiating a second solve. Should be the optimal
                value of the objective function of the first solve.

        Returns
        -------
        None. This method generates attributes for the class.
        """

        self.solved = True
        if 'add_const' in kwargs:
            self.sepInfo(tcancel=self.transformCancel, sub=kwargs['add_const'])
            method = "min"
        else:
            self.sepInfo(tcancel=self.transformCancel)
            method = "max"
        if config.integrality:
            self.result = lpSolve.lp(method, self.obj, self.constraint, self.dir, self.rhs, int_vec=self.intreq)
        else:
            self.result = lpSolve.lp(method, self.obj, self.constraint, self.dir, self.rhs)
        self.solution = self.result.rx2('solution')
    
    def characteristics(self, objective_only=False):
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