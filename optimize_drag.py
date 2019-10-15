import config
import argparse

parser = argparse.ArgumentParser(
    description='A program designed to optimize a given dragon over a particular timeframe.'
)
parser.add_argument('dragon', help='The dragon (or dragons) you desire to optimize or compare. Case sensitive.')
parser.add_argument('-ds', '--displayskill', action='store_true', 
                    help='Forces skill display')
parser.add_argument('-dns', '--displaynoskill', action='store_true', 
                    help='Forces no skill display')
parser.add_argument('-dtc', '--displaytransformcancel', action='store_true', 
                    help='Forces transform cancel display')
parser.add_argument('-c', '--compare', action='store_true',
                    help='Forces breakpoints to be displayed regardless of output type.')
parser.add_argument('-bo', '--bnboverride', action='store_true',
                    help='Overrides the default solution methods to run BnB.')
parser.add_argument('-l', '--leniency', type=int,
                    help='Changes the leniency computed between certain actions.')
parser.add_argument('-s', '--skill', type=float,
                    help='Changes the coefficient used to compute skill damage.')
parser.add_argument('--hull', action='store_true',
                    help='Provides a graph of the optimal damage at each moment up to 600 frames. Omits usual output and overrides other options.')
parser.add_argument('--add', action='append',
                    help='A list of strings that can be input to compute more than one dragon at once. Not well implemented at the moment. Only works with hull')

args = parser.parse_args()

forbidden = ['DyJeanne']
psiren_call = False

if args.dragon in forbidden:
    print('This dragon is lacking data, and cannot be run.')
    print('Exiting program.')
    quit()

if args.dragon == 'Psiren':
    psiren_call = True

if args.add:
    for dragon in args.add:
        if dragon in forbidden:
            print('This dragon is lacking data, and cannot be run.')
            print('Exiting program.')
            quit()
        if dragon == 'Psiren':
            psiren_call = True

yes = ['Y', 'y', 'yes', 'Yes', 'YES']
no = ['n', 'N', 'no', 'No', 'NO']


if not (args.displayskill or args.displaynoskill or args.displaytransformcancel):
    config.disp_mode = 'Default'
else:
    config.disp_mode = []
    if args.displayskill:
        config.disp_mode += ['skill']
    if args.displaynoskill:
        config.disp_mode += ['noskill']
    if args.displaytransformcancel:
        config.disp_mode += ['tcancel']

if args.compare:
    config.disp_compare = True

if args.bnboverride:
    config.bnbOverride = True

if isinstance(args.leniency, int):
    config.leniency = args.leniency

if isinstance(args.skill, float):
    config.skill_coefficient = args.skill

if args.hull and psiren_call:
    print('Hull is not currently compatable with Psiren.')
    confirmation = input('Proceed with a normal solve? [Y/N] : ')
    if confirmation in yes:
        pass
    elif confirmation in no:
        print('Exiting program.')
        quit()
    else:
        print('Input not recognized. Exiting program.')
        quit()

if args.hull and not psiren_call:
    print('This feature is currently not very well developed.')
    print('Depending on your choice of dragon(s), computation may be *very* inefficient and time consuming.')
    confirmation = input('Are you sure you want to continue? [Y/N] : ')
    if confirmation in no:
        print('Exiting program.')
        quit()
    elif confirmation in yes:
        print('Begining Imports.')
        from compute_hull import HullFinder
        print('Done.')
        if args.add:
            hull = HullFinder(args.dragon, additional_dragons=args.add)
        else:
            hull = HullFinder(args.dragon)
        hull.find_hull()
    else:
        print('Input not recognized. Exiting program.')
        quit()

else:
    print('Beginning Imports.')
    from main_solver import Main_Solver
    print('Done.')
    if psiren_call:
        config.bnbOverride = True
        config.initial_time = 13
        config.bound_method = 'None'
    config.dragon = args.dragon
    optimal_solution = Main_Solver()
    optimal_solution.detSolType()
    optimal_solution.solve_problems()
    optimal_solution.zero_problems()
    optimal_solution.display()




