import config
import scipy.optimize as spOpt

def fZero(x, string1, string2, info):
    comboDPS = []
    for combo in [string1, string2]:
        if combo.useSkill:
            comboDPS += [(x*info.damage[-1]/config.skill_coefficient + combo.objective - info.damage[-1])/(combo.duration)]
        else:
            comboDPS += [combo.objective/combo.duration]
    return comboDPS[0] - comboDPS[1]

def rootFind(string1, string2, info):
    if info.damage[-1] != 0:
        zero = round(spOpt.newton(fZero, 1, args=(string1, string2, info)), 3)
    elif string1.objective >= string2.objective: 
        zero = '-Inf'
    elif string1.objective < string2.objective:
        zero = 'Inf'
    return zero