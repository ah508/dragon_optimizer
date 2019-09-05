import config

def fZero(x, skillVal, noskillVal, info):
    skillDPS = (x*info.damage[-1]/config.skill_coefficient + skillVal - info.damage[-1])/(info.time + info.skillTime + info.transformTime)
    noskillDPS = noskillVal/(info.time + info.transformTime)
    return noskillDPS - skillDPS