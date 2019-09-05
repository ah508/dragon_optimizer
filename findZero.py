import config
import scipy.optimize as spOpt

def fZero(x, skillVal, noskillVal, info):
    skillDPS = (x*info.damage[-1]/config.skill_coefficient + skillVal - info.damage[-1])/(info.time + info.skillTime + info.transformTime)
    noskillDPS = noskillVal/(info.time + info.transformTime)
    return noskillDPS - skillDPS

def rootFind(skillVal, noskillVal, info):
    if info.damage[-1] != 0:
        zero = spOpt.newton(fZero, 1, args=(skillVal, noskillVal, info))
    elif skillVal >= noskillVal: 
        zero = '-Inf'
    elif skillVal < noskillVal:
        zero = 'Inf'
    return zero