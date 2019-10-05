import config
from findZero import rootFind
import rpy2
import pandas
from data_refine import Refine
from bnb_formulation import BnBsolution
from lp_solver import LPsolution, SLPsolution
from output import MainDisplay


class Main_Solver:
    # Determines solution type, whether or not to solve, and whether or 
    # not to find the zeros.
    def __init__(self):
        complete_dragons = pandas.read_csv('file:discrete_dragon_data.csv', header=0, index_col=0)
        # Reading the data from the csv with pandas.
        # Should be moved to a different file so it doesn't need to be
        # reread each time.
        self.dragon = complete_dragons.loc[config.dragon]
        self.info = Refine(self.dragon)
        # Data is refined.

    def detSolType(self):
        self.bufferable = False
        for element in self.info.cancels:
            if element != 0:
                self.bufferable = True
                break
        # Ascertaining bufferability.

        self.bnb = (config.bnbOverride or self.bufferable)
        # As of now, if the unit is bufferable, they must be handled by
        # bnb.  This may be rectified in the future.

        if self.bnb:
            self.skill = BnBsolution(self.dragon, 1)
            self.noskill = BnBsolution(self.dragon, 0)
            self.tcancel = BnBsolution(self.dragon, 1, transformCancel=True)

        elif self.info.cond != [1, 0]:
            self.skill = SLPsolution(self.dragon, 0)
            self.noskill = LPsolution(self.dragon, 0)
            self.tcancel = SLPsolution(self.dragon, 1)

        else:
            self.skill = LPsolution(self.dragon, 1)
            self.noskill = LPsolution(self.dragon, 0)
            self.tcancel = LPsolution(self.dragon, 1, transformCancel=1)
        # Solution types are assigned.

    def solve_problems(self):
        # Determining which problems to solve, as specified in config.
        if config.disp_compare or config.disp_mode == 'Default':
            mode_list = ['skill', 'noskill', 'tcancel']
        else:
            mode_list = config.disp_mode

        for mode in mode_list:
            getattr(self, mode).solve()
            if config.obj_strat == 'Min Frames' and not self.bnb:
                getattr(self, mode).characteristics(objective_only=True)
                getattr(self, mode).solve(add_const=getattr(self, mode).objective)
            getattr(self, mode).characteristics()
        # If Min Frames is specified, initiates a second solve to
        # minimize frames after maximizing damage.

    def zero_problems(self):
        # Finds the zero between options, if those options were solved.
        self.zero = ['Not Computed', 'Not Computed', 'Not Computed']
        if self.skill.solved and self.noskill.solved:
            self.zero[0] = rootFind(self.skill, self.noskill)
        if self.noskill.solved and self.tcancel.solved:
            self.zero[1] = rootFind(self.tcancel, self.noskill)
        if self.skill.solved and self.tcancel.solved:
            self.zero[2] = rootFind(self.tcancel, self.skill)

    def display(self):
        # Output.
        final = MainDisplay(self.skill, self.noskill, self.tcancel, self.zero)
        final.output()