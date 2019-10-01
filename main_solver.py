import time
start_time = time.process_time()
start_time2 = time.time()
# time, for timing stuff
import config
from findZero import rootFind
import rpy2
import pandas
from data_refine import Refine
from bnb_formulation import BnBsolution
from lp_solver import LPsolution, SLPsolution
from output import MainDisplay

if not config.suppress_status:
    print('imports finished:')
    print(f'process time: {time.process_time() - start_time}')
    print(f'real time: {time.time() - start_time2}')
    print('-')

class Main_Solver:
    # determines solution type, whether or not to solve, and whether or not to find the zeros
    def __init__(self):
        global start_time
        complete_dragons = pandas.read_csv('file:discrete_dragon_data.csv', header=0, index_col=0)
        # reading the data from the csv with pandas
        # should be moved to a different file so it doesn't need to be reread each time.
        self.dragon = complete_dragons.loc[config.dragon]
        self.info = Refine(self.dragon)
        # data is refined
        if not config.suppress_status:
            print('data formatted:')
            print(f'process time: {time.process_time() - start_time}')
            print(f'real time: {time.time() - start_time2}')
            print('-')

    def detSolType(self):
        global start_time
        self.bufferable = False
        for element in self.info.cancels:
            if element != 0:
                self.bufferable = True
                break
        # ascertaining bufferability

        self.bnb = (config.bnbOverride or self.bufferable)
        # as of now, if the unit is bufferable, they must be handled by bnb
        # this may be rectified in the future

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
        # solution types are assigned

        if not config.suppress_status:
            print('solution type determined:')
            print(f'process time: {time.process_time() - start_time}')
            print(f'real time: {time.time() - start_time2}')
            print('-')

    def solve_problems(self):
        global start_time
        # determining which problems to solve, as specified in config
        # if Min Frames is specified, initiates a second solve to minimize frames after maximizing damage
        if config.disp_compare or config.disp_mode == 'Default':
            attr_list = ['skill', 'noskill', 'tcancel']  
        else:
            attr_list = config.disp_mode

        for attribute in attr_list:
            getattr(self, attribute).solve()
            if config.obj_strat == 'Min Frames' and not self.bnb:
                getattr(self, attribute).characteristics(objective_only=True)
                getattr(self, attribute).solve(add_const=getattr(self, attribute).objective)
            getattr(self, attribute).characteristics()
            # using just "attribute" for the attribute is kind of a sin
            # fix later

        if not config.suppress_status:
            print('solved:')
            print(f'process time: {time.process_time() - start_time}')
            print(f'real time: {time.time() - start_time2}')
            print('-')

    def zero_problems(self):
        global start_time
        # finds the zero between options, if those options were solved for
        self.zero = ['Not Computed', 'Not Computed', 'Not Computed']
        if self.skill.solved and self.noskill.solved:
            self.zero[0] = rootFind(self.skill, self.noskill)
        if self.noskill.solved and self.tcancel.solved:
            self.zero[1] = rootFind(self.tcancel, self.noskill)
        if self.skill.solved and self.tcancel.solved:
            self.zero[2] = rootFind(self.tcancel, self.skill)

        if not config.suppress_status:
            print("zero'd:")
            print(f'process time: {time.process_time() - start_time}')
            print(f'real time: {time.time() - start_time2}')
            print('-')

    def display(self):
        global start_time
        # output
        final = MainDisplay(self.skill, self.noskill, self.tcancel, self.zero)
        final.output()
        
        if not config.suppress_status:
            print('++++++++++')
            print('FINISHED:')
            print(f'process time: {time.process_time() - start_time}')
            print(f'real time: {time.time() - start_time2}')
            print('++++++++++')

