import os
from marshmallow import Schema, fields, validate, ValidationError
import json
from pathlib import Path

dpath = str(Path(__file__).parent) + '/dragons'


unfinished = [
    'Gala Thor',
    'Giovanni',
    'Shishimai',
    'Mini Zodi',
    'Mini Hildy',
    'Horus',
    'Barbatos'
]
forbid_expected = set(['Gala Thor', 'Giovanni', 'Shishimai'])
d_time_expected = set([
    ('Shinobi', 34), 
    ('Andromeda', 34), 
    ('Long Long', 34), 
    ('Gold Fafnir', 34),
    ('Gilgamesh', 34)
])
tdamage_expected_100 = set([
    'Kindling Imp',
    'Wellspring Imp',
    'Astral Imp',
    'Zephyr Imp',
    'Pallid Imp',
    'Fubuki',
    'Tsumuji',
    'Hinata',
    'Hikage',
    'Homura',
    'Moon Drake',
    'Cinder Drake',
    'Snow Drake',
    'Gust Drake',
    'Gloom Drake'
])
tdamage_expected_150 = set([
    'Stribog',
    "Poli'ahu",
    'Unicorn',
    'Ifrit',
    'Vodyanoy',
    'Lindworm',
    'Phoenix',
    'Phoenix(Jank)',
    'Brunhilda',
    'Midgardsormr',
    'Mercury',
    'Zodiark',
    'Jupiter',
    'Stribog',
    'Roc',
    'Halloween Silke',
    'Silver Fafnir',
    'Gold Fafnir',
    'Bronze Fafnir',
    'Silke',
    'Juggernaut',
    'Midgardsormr Zero'
])
tdamage_expected_300 = set([
    'Mym',
    'Super Mym'
])

print('UNIMPLEMENTED')
print('-------------')
for drag in unfinished:
    print(drag)
print('-------------')
print(' ')
input('press any key to continue')
print(' ')

print('FORBIDDEN_CHECK')
print('---------------')
for f in os.listdir(dpath):
    fpath = dpath + '/' + f
    name = f[:-5]
    with open(fpath, 'r') as thefile:
        yobj = json.loads(thefile.read())
    if (yobj['class']['forbidden'] and name not in forbid_expected):
        print('{:<22}  --  UNEXPECTED'.format(name))
    elif (yobj['class']['forbidden'] and name in forbid_expected):
          forbid_expected -= set([name])
if forbid_expected == set():
    print('forbidden clear')
else:
    for uc in forbid_expected:
        print('{:<22}  --  NOT FOUND'.format(uc))   
print('---------------')
print(' ')
input('press any key to continue')
print(' ')

print('T_DAMAGE_CHECK')
print('--------------')
for f in os.listdir(dpath):
    fpath = dpath + '/' + f
    name = name = f[:-5]
    with open(fpath, 'r') as thefile:
        yobj = json.loads(thefile.read())
    d = yobj['T']['ndamage']
    if  d == 1.00 and name not in tdamage_expected_100:
        print('{:<22}  --  UNEXPECTED 1.00'.format(name))
    elif  d == 1.00 and name in tdamage_expected_100:
        tdamage_expected_100 -= set([name])
    if  d == 1.50 and name not in tdamage_expected_150:
        print('{:<22}  --  UNEXPECTED 1.50'.format(name))
    elif  d == 1.50 and name in tdamage_expected_150:
        tdamage_expected_150 -= set([name])
    if  d == 3.00 and name not in tdamage_expected_300:
        print('{:<22}  --  UNEXPECTED 3.00'.format(name))
    elif  d == 3.00 and name in tdamage_expected_300:
        tdamage_expected_300 -= set([name])
if tdamage_expected_100 == set():
    print('1.00 clear')
else:
    for uc in tdamage_expected_100:
        print('{:<22}  --  NOT FOUND  1.00'.format(uc))
if tdamage_expected_150 == set():
    print('1.50 clear')
else:
    for uc in tdamage_expected_150:
        print('{:<22}  --  NOT FOUND  1.50'.format(uc))
if tdamage_expected_300 == set():
    print('3.00 clear')
else:
    for uc in tdamage_expected_300:
        print('{:<22}  --  NOT FOUND  3.00'.format(uc))
print('--------------')
print(' ')
input('press any key to continue')
print(' ')

print('DAMAGE CHECK')
print('------------')
for f in os.listdir(dpath):
    fpath = dpath + '/' + f
    name = name = f[:-5]
    with open(fpath, 'r') as thefile:
        yobj = json.loads(thefile.read())
    for move in yobj:
        if move not in ['class', 'T', 'W', 'D']:
            d = yobj[move]['ndamage']
            if d == 0:
                print('{:<22} -- ZERO DAMAGE {}'.format(name, move))
print('------------')
print(' ')
input('press any key to continue')
print(' ')

print('D_TIME_CHECK')
print('------------')
for f in os.listdir(dpath):
    fpath = dpath + '/' + f
    name = name = f[:-5]
    with open(fpath, 'r') as thefile:
        yobj = json.loads(thefile.read())
    d = yobj['D']['rtime']
    dt = yobj['D']['dtime']
    if d != dt:
        print(f'{name}  -- DODGE MISMATCH')
    if  d != 40:
        if (name, d) not in d_time_expected:
            print('{:<22} -- UNEXPECTED {}'.format(name, d))
        elif (name, d) in d_time_expected:
            d_time_expected -= set([(name, d)])
if d_time_expected == set():
    print('unusual dodge times clear')
else:
    for uc in d_time_expected:
        print('{:<22}  -- NOT FOUND'.format(uc))
print('------------')
print(' ')
input('press any key to continue')
print(' ')

print('MOVE_MISMATCH_CHECK')
print('-------------------')
for f in os.listdir(dpath):
    fpath = dpath + '/' + f
    name = name = f[:-5]
    with open(fpath, 'r') as thefile:
        yobj = json.loads(thefile.read())
    for k, v, in yobj.items():
        if k in ['class', 'T', 'S']:
            continue
        vt = v['rtime']
        dt = v['dtime']
        if vt != dt:
            print('{:<22} MOVE MISMATCH ON {:<4} -- DIFF: {}'.format(name, k, abs(vt-dt)))
print('-------------------')
print(' ')
input('press any key to continue')
print(' ')

print('WAIT_SEVEN_TWENTY')
print('-----------------')
for f in os.listdir(dpath):
    fpath = dpath + '/' + f
    name = name = f[:-5]
    with open(fpath, 'r') as thefile:
        yobj = json.loads(thefile.read())
    if yobj['W']['rtime'] == 720:
        print('{:<22}  --  720'.format(name))
    if yobj['W']['rtime'] == 0 or yobj['W']['dtime'] == 0:
        print('{:<22}  --  missing wait'.format(name))
print('-----------------')
print(' ')
input('press any key to continue')
print(' ')