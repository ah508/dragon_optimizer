from pathlib import Path
import json

def fetch_dragon(dname):
    path = str(Path(__file__).parent) + '/dragons/' + dname + '.json'
    with open(path) as f:
        dragon = json.loads(f.read())
    return dragon

def fetch_key(dragclass):
    if dragclass['forbidden']:
        raise NotImplementedError('Dragon not implemented')
    tempname = dragclass['key']
    return tempname

def load_data(key, model):
    path1 = str(Path(__file__).parent / 'lptemplates' / (key + '.json'))
    path2 = str(Path(__file__).parent / 'lptemplates' / 'lpfiles' / (key + '.lp'))
    try:
        with open(path1) as f:
            template = json.loads(f.read())
        model.read(path2)
    except FileNotFoundError:
        raise NotImplementedError(f'Template {key} not implemented')
    return template