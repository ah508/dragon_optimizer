import math
import os
import json

def haste_sp(move, modifier):
    return math.ceil(move['sp']*(1 + modifier))

def find_speed(move, base, modifier):
    if move in ['T', 'D', 'BD']:
        return base
    return math.ceil(base/(1 + modifier))

def get_duration(dragon, move, speed, bufftime):
    bstart = find_speed(move, dragon[move]['effect']['timing'], speed)
    skend = find_speed(move, dragon[move]['rtime'], speed)
    buff_dur = dragon[move]['effect']['duration']*(1 + bufftime)
    return buff_dur - skend + bstart

#NOTE: may get replaced depending on behavior of model.vars
def get_model_variables(model, state_tree, getIndex):
    ref_vec = [0] * state_tree['size']
    for state in state_tree:
        if state == 'size':
            continue
        for move in state_tree[state]:
            index = getIndex(state, move)
            ref_vec[index] = model.var_by_name(state+move)
    return ref_vec

def apply_boost(stats, effect):
    if isinstance(effect['type'], list):
        for i in range(len(effect['type'])):
            if effect['type'][i] in ['bog', 'energized', 'inspired']:
                stats[effect['type']] = True
            else:
                stats[effect['type']] += effect['value'][i]
    elif effect['type']:
        if effect['type'] in ['bog', 'energized', 'inspired']:
            stats[effect['type']] = True
        else:
            stats[effect['type']] += effect['value']

def make_dformula(mode):
    if mode == 'puremod':
        def dformula(stats, base_mod, atype):
            return base_mod
    else:
        def dformula(stats, base_mod, atype, energized=True, inspired=True):
            if stats['inspired'] and atype == 's' and inspired:
                critc = 1
            else:
                critc = min(stats['critchance'], 1)
            if atype == 's':
                if stats['energized'] and energized:
                    pskd = stats['passiveskd'] + 0.5
                else:
                    pskd = stats['passiveskd']
                skdcoeff = (
                    (1 + pskd)
                    *(1 + stats['buffskd'])
                    *(1 + stats['coabskd'])
                )
            else:
                skdcoeff = 1
            # if atype == 'f':
            #     fscoeff = (
            #         (1 + stats['passivefs'])
            #         *(1 + stats['activefs'])
            #         *(1 + stats['coabfs'])
            #     )
            # else:
            #     fscoeff = 1
            if stats['broken']:
                breakcoeff = stats['breakmod']
                bpun = stats['brokepun']
            else:
                breakcoeff = 1
                bpun = 1
            critcoeff = critc*(1.7 + stats['critmod'])
            puncoeff = stats['afflicpun']*bpun
            strcoeff = (
                stats['basestr']
                *(1 + stats['passivestr'])
                *(1 + stats['activestr'])
                *(1 + stats['coabstr'])
            )
            defcoeff = (
                stats['basedef']
                *max((1-stats['defmod']), 0.5)
                *breakcoeff
            )
            damage = (
                (5/3)
                *strcoeff
                *base_mod
                *critcoeff
                *puncoeff
                *skdcoeff
                # *fscoeff
                *stats['eleadv']
                *stats['dboost']
                /defcoeff
            )
            if stats['bog']:
                damage *= 1.5
            return round(damage, 2)
    return dformula

def get_state_values(state_order, template, dragon, stats, getIndex, dformula):
    state_tree = template['state tree']
    obj_len = state_tree['size']
    real_time = [0] * obj_len
    drag_time = [0] * obj_len
    real_damage = [0] * obj_len
    sp_gen = [0] * obj_len
    for state in state_order:
        hold = []
        for move in state_tree[state]:
            index = getIndex(state, move)
            drag_time[index] = find_speed(move, 
                                          dragon[move]['dtime'], 
                                          stats['aspd'])
            real_time[index] = find_speed(stats,
                                          dragon[move]['rtime'],
                                          stats['aspd'])
            real_damage[index] = dformula(stats, 
                                          dragon[move]['ndamage'], 
                                          dragon[move]['type'])
            sp_gen[index] = haste_sp(dragon[move], stats['ahst'])

            if dragon[move]['bdamage'] and move != template['boost on']:
                real_damage[index] += dformula(stats, 
                                               dragon[move]['bdamage'], 
                                               dragon[move]['type'])
            elif dragon[move]['bdamage'] and move == template['boost on']:
                hold.append(index)
                hold.append(dragon[move]['bdamage'])
                hold.append(dragon[move]['type'])

        if template['boost on']:
            apply_boost(stats, dragon[template['boost on']]['effect'])
            if hold:
                real_damage[hold[0]] += dformula(stats, hold[1], hold[2])

    return {
        'frames' : drag_time,
        'realframes': real_time,
        'damage' : real_damage,
        'sp' : sp_gen
    }

def generate_state_stats(template, dragon, infoset, getIndex):
    dformula = make_dformula(infoset['mode'])
    stats = infoset['stats']
    if infoset['mode'] == 'effmod':
        stats['basestr'] = 1
    
    state_values = get_state_values(template['state order'], 
                                    template, 
                                    dragon, 
                                    stats, 
                                    getIndex,
                                    dformula)
    if template['boost on']:
        # NOTE: if the buff is attack speed, this results in inaccurate handling
        # this can be fixed with relative ease, for whoever next works on this
        state_values['buff duration'] = get_duration(dragon, 
                                                     template['boost on'], 
                                                     stats['aspd'],
                                                     stats['bufftime'])
    state_values['transform time'] = infoset['transform time']
    state_values['skill'] = min(dragon['class']['skill'], infoset['skill'])
                            
    return state_values

