import time
import mip
from marshmallow import Schema, fields, validate, ValidationError
from file_fetchers import fetch_dragon, fetch_key, load_data
from data_refine import generate_state_stats, get_model_variables
from build_methods import make_getIndex
from lp_solver import set_model_constraints, solve_model

def solve(infoset, output=True):
    startttime = time.time()
    model = mip.Model()
    drg = infoset['dragon']
    dragon = fetch_dragon(drg)
    temp_key = fetch_key(dragon['class'])
    template = load_data(temp_key, model)
    getIndex = make_getIndex(template['state tree'])
    ref_vec = get_model_variables(model, template['state tree'], getIndex)
    state_values = generate_state_stats(template, dragon, infoset, getIndex)
    set_model_constraints(model, ref_vec, template, state_values, getIndex)
    solution = solve_model(model, ref_vec, state_values, output=output, relaxation=infoset['relax'])
    solution['rules'] = template['rules']
    solvetime = time.time() - startttime
    solution['solvetime'] = solvetime
    return solution

class StatSchema(Schema):
    basestr = fields.Integer(missing=1000, validate=validate.Range(min=0, max=100000))
    standatk = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    passivestr = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    activestr = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    coabstr = fields.Float(missing=0, validate=validate.Range(min=0, max=0.2))
    passiveskd = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    activeskd = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    coabskd = fields.Float(missing=0, validate=validate.Range(min=0, max=0.3))
    passivefs = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    activefs = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    coabfs = fields.Float(missing=0, validate=validate.Range(min=0, max=0.4))
    critchance = fields.Float(missing=0, validate=validate.Range(min=0, max=1))
    critmod = fields.Float(missing=0, validate=validate.Range(min=-1.7, max=5))
    afflicpun = fields.Float(missing=0, validate=validate.Range(min=-1, max=5))
    breakpun = fields.Float(missing=0, validate=validate.Range(min=-100, max=10))
    breakmod = fields.Float(missing=0.6, validate=validate.Range(min=1e-2, max=100))
    basedef = fields.Float(missing=10, validate=validate.Range(min=1e-2, max=100))
    defmod = fields.Float(missing=0, validate=validate.Range(min=0, max=0.5))
    eleres = fields.Float(missing=0, validate=validate.Range(min=-5, max=5))
    aspd = fields.Float(missing=0, validate=validate.Range(min=-5, max=5))
    ahst = fields.Float(missing=0, validate=validate.Range(min=-5, max=5))
    eleadv = fields.Float(missing=1, validate=validate.Range(min=0, max=5))
    dboost = fields.Float(missing=0.2, validate=validate.Range(min=0, max=5))
    energized = fields.Bool(missing=False)
    inspired = fields.Bool(missing=False)
    broken = fields.Bool(missing=False)
    bog = fields.Bool(missing=False)
    bufftime = fields.Float(missing=0, validate=validate.Range(min=0, max=100))

class InputSchema(Schema):
    dragon = fields.String(
        required=True, 
        error_messages={"required": "dragon is required"},
        validate=[
            validate.Length(max=40),
            validate.NoneOf([
                'Gala Thor',
                'Giovanni',
                'Shishimai',
                'Horus',
                'Mini Hildy',
                'Mini Zodi',
                'Barbatos'
            ])
        ]
    )
    mode = fields.String(
        required=True, 
        error_messages={"required": "mode is required"},
        validate=validate.OneOf(['puremod', 'effmod', 'damage'])
    )
    transform_time = fields.Integer(
        required=True, 
        error_messages={"required": "transformation time is required"},
        data_key="transform time",
        validate=validate.Range(min=1, max=12000)
    )
    skill = fields.Integer(
        required=True, 
        error_messages={"required": "skill is required"},
        validate=validate.OneOf([0, 1])
    )
    relax = fields.Bool(missing=False)
    leniency = fields.Integer(missing=0)
    stats = fields.Nested(StatSchema)

if __name__ == "__main__":
    faux_infoset = {
        'dragon' : 'High Brunhilda',
        'mode' : 'effmod',
        'relax' : False,
        'leniency' : 0,
        'transform time' : 600,
        'skill' : 1,
        'stats' : {
            'basestr' : 100,
            'passivestr' : 0,
            'activestr' : 0,
            'coabstr' :  0,
            'passiveskd' : 0,
            'activeskd' : 0,
            'coabskd' : 0,
            'critchance' : 0,
            'critmod' : 0,
            'afflicpun' : 0,
            'breakmod' : 0.6,
            'breakpun' : 0,
            'basedef' : 10,
            'defmod' : 0,
            'eleres' : 0,
            'aspd' : 0, 
            'ahst' : 0,
            'eleadv' : 1,
            'dboost' : 0,
            'energized' : False,
            'inspired' : False,
            'broken' : False,
            'bog' : False,
            'bufftime' : 0
        }
    }
    
    testschema = InputSchema()
    out = testschema.load(faux_infoset)
    print(out)
    solve(out)
