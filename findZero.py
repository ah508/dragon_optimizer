import config
import scipy.optimize as spOpt

def fZero(x, string1, string2):
    comboDPS = []
    for combo in [string1, string2]:
        if combo.useSkill:
            comboDPS += [(x*combo.damage[-1]/config.skill_coefficient + combo.objective - combo.damage[-1])/(combo.duration)]
        else:
            comboDPS += [combo.objective/combo.duration]
    return comboDPS[0] - comboDPS[1]

def rootFind(string1, string2):
    if string1.damage[-1] != 0:
        zero = round(spOpt.newton(fZero, 1, args=(string1, string2)), 3)
    elif string1.objective >= string2.objective: 
        zero = '-Inf'
    elif string1.objective < string2.objective:
        zero = 'Inf'
    return zero