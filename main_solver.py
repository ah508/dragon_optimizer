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

print('imports finished:')
print(time.process_time() - start_time)
print('-')

# complete_dragons = pandas.read_csv('file:dragon_optimizer/discrete_dragon_data.csv', header=0, index_col=0)
complete_dragons = pandas.read_csv('file:discrete_dragon_data.csv', header=0, index_col=0)
dragon = complete_dragons.loc[config.dragon]

info = Refine(dragon)

print('data formatted:')
print(time.process_time() - start_time)
print('-')

bufferable = False
for element in info.cancels:
    if element != 0:
        bufferable = True
        break

bnb = (config.bnbOverride or bufferable)

if bnb:
    info.adjacencyGen()
    skill = BnBsolution(info, 1)
    noskill = BnBsolution(info, 0)
    tcancel = BnBsolution(info, 1, tCancel=True)

elif info.cond != [1, 0]:
    skill = SLPsolution(info, 1)
    noskill = LPsolution(info, 0)
    tcancel = SLPsolution(info, 1)

else:
    skill = LPsolution(info, 1)
    noskill = LPsolution(info, 0)
    tcancel = LPsolution(info, 0) 

print('solution type determined:')
print(time.process_time() - start_time)
print('-')

if config.disp_compare or config.disp_mode in ['Default', 'Full List']:
    skill.solve()
    noskill.solve()
    tcancel.solve()
    if config.obj_strat == 'Min Frames' and not bnb:
        noskill.characteristics(objective_only=True)
        noskill.solve(add_const=noskill.objective)
        skill.characteristics(objective_only=True)
        skill.solve(add_const=skill.objective)
        tcancel.characteristics(objective_only=True)
        tcancel.solve(add_const=tcancel.objective)

elif config.disp_mode == 'Skill':
    skill.solve()
    if config.obj_strat == 'Min Frames' and not bnb:
        skill.characteristics(objective_only=True)
        skill.solve(add_const=skill.objective)

elif config.disp_mode == 'No Skill':
    noskill.solve()
    if config.obj_strat == 'Min Frames' and not bnb:
        noskill.characteristics(objective_only=True)
        noskill.solve(add_const=noskill.objective)

elif config.disp_mode == 'Transform Cancel':
    tcancel.solve()
    if config.obj_strat == 'Min Frames' and not bnb:
        tcancel.characteristics(objective_only=True)
        tcancel.solve(add_const=tcancel.objective)

skill.characteristics()
noskill.characteristics()
tcancel.characteristics(tCancel=True)

print('solved:')
print(time.process_time() - start_time)
print('-')

zero = ['Not Computed', 'Not Computed', 'Not Computed']
if skill.solved and noskill.solved:
    zero[0] = rootFind(skill, noskill, info)
if noskill.solved and tcancel.solved:
    zero[1] = rootFind(tcancel, noskill, info)
if skill.solved and tcancel.solved:
    zero[2] = rootFind(tcancel, skill, info)

print("zero'd:")
print(time.process_time() - start_time)
print('-')

final = MainDisplay(skill, noskill, tcancel, info, zero)
final.output()


print('++++++++++')
print('FINISHED:')
print(time.process_time() - start_time)
print('++++++++++')
