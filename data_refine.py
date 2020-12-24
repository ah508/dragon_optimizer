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
    if dragon[move]['effect']['duration'] == 'inf':
        return 'inf'
    if dragon[move]['effect']['type'] in ['bog', 'defmod', 'eleres']:
        return dragon[move]['effect']['duration']
        # this is a hacked way of doing it. 
        # would be best to have a "extendable" parameter in dragon definition.
        # that has the added benefit of curtailing buffzones
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
                stats[effect['type'][i]] = True
            else:
                stats[effect['type'][i]] += effect['value'][i]
    elif effect['type']:
        if effect['type'] in ['bog', 'energized', 'inspired']:
            stats[effect['type']] = True
        else:
            stats[effect['type']] += effect['value']

def make_dformula(mode):
    if mode == 'puremod':
        def dformula(stats, base_mod, atype):
            return base_mod
    elif mode == 'effmod':
        # this expansion is messy, but I don't want to need to do the comparison in function
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
                    *(1 + stats['activeskd'])
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
                bpun = stats['breakpun']
            else:
                breakcoeff = 1
                bpun = 1
            elerescoeff = 1 + stats['eleres']
            critcoeff = 1 + critc*(0.7 + stats['critmod'])
            puncoeff = (1 + stats['afflicpun'])*bpun
            strcoeff = (
                stats['basestr']
                *(1 + stats['passivestr'])
                *(1 + stats['activestr'])
                *(1 + stats['coabstr'])
            )
            defcoeff = (
                max((1-stats['defmod']), 0.5)
                *breakcoeff
            )
            damage = (
                elerescoeff
                *strcoeff
                *base_mod
                *critcoeff
                *puncoeff
                *skdcoeff
                # *fscoeff
                *stats['eleadv']
                *(1 + stats['dboost'])
                /defcoeff
            )
            if stats['bog']:
                damage *= 1.5
            return round(damage, 2)
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
                    *(1 + stats['activeskd'])
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
            elerescoeff = 1 + stats['eleres']
            critcoeff = 1 + critc*(0.7 + stats['critmod'])
            print(critcoeff)
            puncoeff = (1 + stats['afflicpun'])*bpun
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
                *elerescoeff
                *strcoeff
                *base_mod
                *critcoeff
                *puncoeff
                *skdcoeff
                # *fscoeff
                *stats['eleadv']
                *(1 + stats['dboost'])
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
    for group in state_order:
        hold = []
        for state in group:
            temp = {}
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
                    temp['index'] = index
                    temp['bdamage'] = dragon[move]['bdamage']
                    temp['type'] = dragon[move]['type']
                    hold.append(temp)

        if template['boost on']:
            apply_boost(stats, dragon[template['boost on']]['effect'])
            if hold:
                for held in hold:
                    real_damage[held['index']] += dformula(stats, held['bdamage'], held['type'])

    return {
        'frames' : drag_time,
        'realframes': real_time,
        'damage' : real_damage,
        'sp' : sp_gen
    }

def generate_state_stats(template, dragon, infoset, getIndex):
    dformula = make_dformula(infoset['mode'])
    stats = infoset['stats']
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
    state_values['transform time'] = infoset['transform time'] - infoset['leniency']
    state_values['skill'] = min(dragon['class']['skill'], infoset['skill'])
                            
    return state_values

