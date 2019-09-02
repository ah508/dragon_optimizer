import pandas
import math
import numpy as np
import rpy2
import rpy2.robjects as robjects
import config
from fractions import Fraction
from data_refine import Refine, Constraints, SolInfo



#DEFUNCT
# to be removed at a later date.



# complete_dragons = pandas.read_csv('file:dragon_optimizer/discrete_dragon_data.csv', header=0, index_col=0)
complete_dragons = pandas.read_csv('file:C:/Users/Adam/Documents/GACHAAAAA/Optimization/dragon_optimizer/discrete_dragon_data.csv', header=0, index_col=0)
dragon = complete_dragons.loc[config.dragon]

# refCombo = ['T  ', 'C1a', 'C1b', 'C2a', 'C2b', 'C3a', 'C3b', 'C4a', 'C4b', 'C5a', 'C5b', 'W  ', 'D  ', 'S  ']
# damage = [150] + [dragon[9 + 4*i] for i in range(0, 10)] + [0, 0] + [dragon['Skill Damage']*config.skill_coefficient]
# cancels = [0] + [dragon[11 + 4*i] for i in range(0, 10)] + [0, 0, 0]
# cooldown = [0] + [dragon[12 + 4*i] for i in range(0, 10)] + [0, 0, 0,]
# lastC = [i for i, e in enumerate(cooldown) if e != 0]
# frameC = [0] + [dragon[10 + 4*i] for i in range(0, 10)] + [cooldown[lastC[-1]]] + [dragon['Dodge Frames']] + [0]
# tCancel = dragon['Transform Cancel']

# delVec = []
# for i in range(1, len(damage)-3):
#     if [damage[i], cancels[i], cooldown[i], frameC[i]] == [0, 0, 0, 0]:
#         delVec += [i]
# delVec.reverse()
# for vector in [damage, cancels, cooldown, frameC, refCombo]:
#     for indices in delVec:
#         del vector[indices]

# reflength = len(refCombo)

# if type(dragon['Skill Effect']) == str:
#     sEffect = float(Fraction(dragon['Skill Effect']))
# else:
#     sEffect = dragon['Skill Effect']
# cond = [sEffect, dragon['Effect Time']]

info = Refine(dragon)
info.trimmed()

bufferable = False
for element in info.cancels:
    if element != 0:
        bufferable = True
        break
        

mode = 'Default'
if info.cond != [1, 0] or bufferable:
    mode = 'BnB'
elif info.tCancel:
    mode = 'Transform Cancel'
#note: this breaks jeanne.
if config.bnbOverride:
    mode = 'BnB'


# timeMod = config.initial_time*60*(1 + dragon['DragonTime'] + config.additional_time)
# leniency = config.leniency
# frameC[-1] += leniency
# frameC[-2] += leniency
# tTime = dragon['Transformation']
# sTime = dragon['Skill Duration']
# waitCheck = list(np.zeros(reflength))
# waitCheck[-3] = 1
# waitCheck[-4] = -1

# if config.attack_rate != 1:
#     for i in range(1, reflength-3):
#         frameC[i] = math.ceil(frameC[i]/config.attack_rate)
#     sTime = math.ceil(sTime/config.attack_rate)
info.speedCheck()

# constraint = [1] + list(np.zeros(reflength-2))
# direction = ['==']
# for cascade in range(1, reflength-4):
#     constraint += list(np.zeros(cascade+1)) + [-1, 1] + list(np.zeros(reflength-cascade-3))
#     direction += ['<=']
# constraint += [0]
# for limiters in range(1, reflength):
#     constraint += list(np.zeros(limiters)) + [1] + list(np.zeros(reflength-limiters-1))
#     direction += ['>=']
# constraint += [0, 1] + list(np.zeros(reflength-5)) + [-1, -1, -1]
# constraint += waitCheck
# constraint += list(np.zeros(reflength-1)) + [1]
# constraint += frameC
# direction += ['<=', '<=', '<=', '<=']
lpConstraints = Constraints(info.rlength, info.frames)
lpConstraints.rowGeneration()

# rowcount = 2*reflength - 1
# r_obj = robjects.FloatVector(damage)
# intreq = robjects.IntVector(range(1, len(damage)))
# r_const = robjects.r['matrix'](constraint, nrow=rowcount, byrow=True)
# r_dir = robjects.StrVector(direction)
# rhs = [1] + list(np.zeros(reflength-5))
# skillAppend = [1, 0, 1, timeMod]
# noskillAppend = [1, 0, 0, timeMod]
# rhsFiller = list(np.zeros(reflength-1))
solverInfo = SolInfo(info, lpConstraints)


adjacency = info.adjacencyGen()
# adjacency = np.full([reflength, reflength], -1)
# for i in range(0, reflength):
#     for j in range(0, reflength):
#         if i == 0 and j >= reflength-3:
#             if j == reflength-1:
#                 adjacency[i][j] = frameC[j] 
#         elif i >= reflength-3 and j == 1:
#             adjacency[i][j] = frameC[j] 
#         elif i < reflength-3 and j >= reflength-2:
#             adjacency[i][j] = frameC[j] 
#             if j == reflength-2 and cancels[i] != 0:
#                 adjacency[i][j] += cancels[i] - leniency
#         elif i in range(0, reflength-3) and j == i+1:
#             adjacency[i][j] = frameC[j]