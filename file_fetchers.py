import os
import json

def fetch_dragon(dname):
    with open(os.getcwd() + '/dragons/' + dname + '.json') as f:
        dragon = json.loads(f.read())
    return dragon

def fetch_key(dragclass):
    if dragclass['forbidden']:
        raise NotImplementedError('Dragon not implemented')
    tempname = dragclass['key']
    return tempname

def load_data(key, model):
    path = os.getcwd() + '/lptemplates/'
    try:
        with open(path + key + '.json') as f:
            template = json.loads(f.read())
        model.read(path + 'lpfiles/' + key + '.lp')
    except FileNotFoundError:
        raise NotImplementedError(f'Template {key} not implemented')
    return template