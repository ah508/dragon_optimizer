import config
import data_coercion as dc
import numpy as np
import scipy.optimize as spOpt
from data_coercion import reflength as reflength


def fZero(x, solSkill, solNone, damage, time, timeADD, skillDur, selection):
    if selection == 'Compare':
        skillCoeff = 1
    else: skillCoeff = config.skill_coefficient
    
    skill_damage = ((damage[-1]/skillCoeff)*(x) + (solSkill - damage[-1]))/(time + timeADD + skillDur)
    noskill_damage = solNone/(time + timeADD)
    if selection == 'Zero':
        return noskill_damage - skill_damage
    elif selection == 'Compare':
        return skill_damage, noskill_damage

def dparser(skill_damage, noskill_damage, skill_objective, noskill_objective, skill_solution, noskill_solution, **kwargs):
    print("\n")
    print(config.disp_mode)
    if dc.damage[-1] != 0:
        zero = spOpt.newton(fZero, 1, args=(skill_objective, noskill_objective, dc.damage, dc.timeMod, dc.tTime, dc.sTime, 'Zero'))
    elif skill_damage >= noskill_damage: 
        zero = '-Inf'
    elif skill_damage < noskill_damage:
        zero = 'Inf'

    sDuration = round((dc.timeMod + dc.tTime + dc.sTime)/60, 3)
    nsDuration = round((dc.timeMod + dc.tTime)/60, 3)

    if config.disp_mode == 'Both':
        print('Skill Optimum: ')
        if 'opt_sk_str' in kwargs:
            ddisplay(skill_solution, skill_damage, skill_objective, zero, sDuration, optimal_string=kwargs['opt_sk_str'])
        else: ddisplay(skill_solution, skill_damage, skill_objective, zero, sDuration)
        print('No Skill Optimum:')
        if 'opt_nosk_str' in kwargs:
            ddisplay(noskill_solution, noskill_damage, noskill_objective, zero, nsDuration, optimal_string=kwargs['opt_nosk_str'])
        else: ddisplay(noskill_solution, noskill_damage, noskill_objective, zero, nsDuration)

    elif (skill_damage >= noskill_damage and config.disp_mode != 'No Skill') or config.disp_mode == 'Skill':
        if skill_damage >= noskill_damage:
            print('Skill is Always Optimal.')
        print('Skill Optimum:')
        if 'opt_sk_str' in kwargs:
            ddisplay(skill_solution, skill_damage, skill_objective, zero, sDuration, optimal_string=kwargs['opt_sk_str'])
        else: ddisplay(skill_solution, skill_damage, skill_objective, zero, sDuration)

    elif (skill_damage < noskill_damage and config.disp_mode != 'Skill') or config.disp_mode == 'No Skill':
        if skill_damage < noskill_damage:
            print('Skill is a Loss.')
        print('No Skill Optimum:')
        if 'opt_nosk_str' in kwargs:
            ddisplay(noskill_solution, noskill_damage, noskill_objective, zero, nsDuration, optimal_string=kwargs['opt_nosk_str'])
        else: ddisplay(noskill_solution, noskill_damage, noskill_objective, zero, nsDuration)


def ddisplay(solution, damage, objective, zero, duration, **kwargs):
    lenience = dc.timeMod - np.dot(dc.frameC, solution)
    if 'optimal_string' not in kwargs:
        print('__________')
        for i in range(0, len(solution)):
            if (i < reflength-3 and solution[i] != 0 and dc.damage[i] != 0) or i >= reflength-3:
                print(f'{dc.refCombo[i]} :  {solution[i]}')
        print('‾‾‾‾‾‾‾‾‾‾')
    elif 'optimal_string' in kwargs:
        print('___')
        for i in kwargs['optimal_string']:
            if dc.refCombo[i] in ['T  ', 'W  ', 'D  ', 'S  ']:
                print(f'{dc.refCombo[i]}')
            else:
                print(f'{dc.refCombo[i]} ', end=' ')
        print('\n‾‾‾')
    print('____________________________________________________')
    print(f'MOD/s                        |   {60*damage}')
    print(f'Total Mod                    |   {objective}')
    print(f'Skill Coefficient Breakpoint |   {zero}')
    print(f'Leniency                     |   {lenience} f')
    print(f'Duration                     |   {duration} s')
    print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
    print(' ')
    return 