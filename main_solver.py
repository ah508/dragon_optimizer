import time
start_time = time.process_time()

import config
from findZero import rootFind
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import pandas
from data_refine import Refine
from bnb_formulation import BnBsolution
import pybnb
import copy
from lp_solver import LPsolution, SLPsolution
from output import MainDisplay

if not config.suppress_status:
    print('imports finished:')
    print(time.process_time() - start_time)
    print('-')

class Main_Solver:
    def __init__(self):
        global start_time
        complete_dragons = pandas.read_csv('file:discrete_dragon_data.csv', header=0, index_col=0)
        self.dragon = complete_dragons.loc[config.dragon]
        self.info = Refine(self.dragon)
        if not config.suppress_status:
            print('data formatted:')
            print(time.process_time() - start_time)
            print('-')

    def detSolType(self):
        global start_time
        self.bufferable = False
        for element in self.info.cancels:
            if element != 0:
                self.bufferable = True
                break

        self.bnb = (config.bnbOverride or self.bufferable)

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
            self.tcancel = LPsolution(self.dragon, 0) 

        if not config.suppress_status:
            print('solution type determined:')
            print(time.process_time() - start_time)
            print('-')

    def solve_problems(self):
        global start_time
        if config.disp_compare or config.disp_mode in ['Default', 'Full List']:
            self.skill.solve()
            self.noskill.solve()
            self.tcancel.solve()
            if config.obj_strat == 'Min Frames' and not self.bnb:
                self.noskill.characteristics(objective_only=True)
                self.noskill.solve(add_const=self.noskill.objective)
                self.skill.characteristics(objective_only=True)
                self.skill.solve(add_const=self.skill.objective)
                self.tcancel.characteristics(objective_only=True)
                self.tcancel.solve(add_const=self.tcancel.objective)

        elif config.disp_mode == 'Skill':
            self.skill.solve()
            if config.obj_strat == 'Min Frames' and not self.bnb:
                self.skill.characteristics(objective_only=True)
                self.skill.solve(add_const=self.skill.objective)

        elif config.disp_mode == 'No Skill':
            self.noskill.solve()
            if config.obj_strat == 'Min Frames' and not self.bnb:
                self.noskill.characteristics(objective_only=True)
                self.noskill.solve(add_const=self.noskill.objective)

        elif config.disp_mode == 'Transform Cancel':
            self.tcancel.solve()
            if config.obj_strat == 'Min Frames' and not self.bnb:
                self.tcancel.characteristics(objective_only=True)
                self.tcancel.solve(add_const=self.tcancel.objective)

        self.skill.characteristics()
        self.noskill.characteristics()
        self.tcancel.characteristics(tCancel=True)

        if not config.suppress_status:
            print('solved:')
            print(time.process_time() - start_time)
            print('-')

    def zero_problems(self):
        global start_time
        self.zero = ['Not Computed', 'Not Computed', 'Not Computed']
        if self.skill.solved and self.noskill.solved:
            self.zero[0] = rootFind(self.skill, self.noskill)
        if self.noskill.solved and self.tcancel.solved:
            self.zero[1] = rootFind(self.tcancel, self.noskill)
        if self.skill.solved and self.tcancel.solved:
            self.zero[2] = rootFind(self.tcancel, self.skill)

        if not config.suppress_status:
            print("zero'd:")
            print(time.process_time() - start_time)
            print('-')

    def display(self):
        global start_time
        final = MainDisplay(self.skill, self.noskill, self.tcancel, self.zero)
        final.output()
        
        if not config.suppress_status:
            print('++++++++++')
            print('FINISHED:')
            print(time.process_time() - start_time)
            print('++++++++++')

