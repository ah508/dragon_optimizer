import config
import scipy.optimize as spOpt

def fZero(x, skill, noskill, info):
    skillDPS = (x*info.damage[-1]/config.skill_coefficient + skill.objective - info.damage[-1])/(skill.duration)
    noskillDPS = noskill.objective/noskill.duration
    return noskillDPS - skillDPS

def rootFind(skill, noskill, info):
    if info.damage[-1] != 0:
        zero = spOpt.newton(fZero, 1, args=(skill, noskill, info))
    elif skill.objective >= noskill.objective: 
        zero = '-Inf'
    elif skill.objective < noskill.objective:
        zero = 'Inf'
    return zero