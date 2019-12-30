import config
config.suppress_status = True
config.bnb_override = False
config.disp_compare = False
config.obj_strat = 'Default'
# these need to be set in advance to prevent errors
import time
from main_solver import MainSolver
import matplotlib.pyplot as plt


class HullFinder:
    """Computes a 'feasible region' for a list of dragons.

    Strictly speaking, it doesn't actually produce the feasible region
    since there are more decision variables than is convinient to
    display. However, the figure is analagous to the feasible region,
    plotting the optimal value of the objective function with respect
    to time, our limited resource.

    NOTE: This feature is currently hacked together and poorly
    implemented. The computation is sloppy, slow, and in some cases
    prohibitively expensive. The documentation will be sparse, and
    likely not very clear. For the time being, only make use of this
    if you know what you are doing.

    NOTE: Do not try to use this feature for bufferable dragons.

    Attributes
    ----------
    dragons : [str]
        A list of the names of the dragons to be compared.
    warehouse : {str : class instance}
        A dictionary used to store the results for each dragon.
    start_time : float
        The time at which the process starts.
    Storage : class
        Used to make it a bit easier to loop over the results.

    Parameters
    ----------
    dragon : str
        The name of the dragon that you wish to find the 'hull' of.
    additional_dragons : [str](=[])
        A list of the names of any additional dragons to be
        computed.
    """
    
    def __init__(self, dragon, additional_dragons=[]):
        self.dragons = [dragon] + additional_dragons
        self.warehouse = {}
        self.start_time = time.process_time()
        print('Timing starts now.')
        # warehouse is a terrible variable name

    class Storage:
        """Used to... store... things....

        This could be achieved in some other way, but making
        the storage object a class makes it easier to work with later.

        Attributes
        ----------
        leaves : list
            A list to which the optimal result and corresponding
            time will be appended.
        solution_set : class instance
            An instance of MainSolver corresponding to the current
            dragon. This is not immediately initialized, but it does
            exist.
            note to self: should take the dragon in question as
            a parameter.
        """

        def __init__(self):
            self.leaves = []

    def find_hull(self):
        """Finds the 'hull.'

        Loops over all of the requested dragons, and all of the
        desired solution methods, computing the optimal solution
        for every frame between 0 and 600, and then displays
        comparisons of the results with shaded polygons.

        Parameters
        ----------
        None. This method uses attributes of the class.

        Returns
        -------
        None. Output is plotted.

        TODO: 
            methods for leniency comparisons.
            maybe reduce the functionality here, and plot elsewhere
            clean up variable names
            clean up storage implementation
            make some sweeping changes elsewhere and do this all
            dynamically
        """

        for creature in self.dragons:
            config.dragon = creature
            if config.disp_mode == 'Default':
                attr_list = ['skill']
            else:
                attr_list = config.disp_mode
            for mode in attr_list:
                magic_key = creature + ' + ' + mode
                config.disp_mode = [mode]
                self.warehouse[magic_key] = self.Storage()
                self.warehouse[magic_key].solution_set = MainSolver()
                self.warehouse[magic_key].solution_set.detSolType()
                for i in range(0, 600):
                    getattr(self.warehouse[magic_key].solution_set, mode).time = i
                    self.warehouse[magic_key].solution_set.solve_problems()
                    self.warehouse[magic_key].leaves.append([getattr(self.warehouse[magic_key].solution_set, mode).objective, i])
            # finding the optimal solution for every time moment between 0 and 600
            # this is a terrible way to handle this BUT - it works for now.
            # I'll find some way to make it smoother later
            print('Segment')
            print(time.process_time() - self.start_time)
            print('-')
        
        for entity in self.warehouse.values():
            entity.leafs = sorted(entity.leaves, key=lambda l:l[1])
            entity.hulld = []
            entity.hullf = []
            for point in entity.leafs:
                entity.hulld.append(point[0])
                entity.hullf.append(point[1])
            entity.hullf.append(600)
            entity.hullf.append(600)
            entity.hullf.append(0)
            entity.hulld.append(max(entity.hulld))
            entity.hulld.append(0)
            entity.hulld.append(0)
            # determining the vertices - this is what lets us display the polygon below

        print('Done!')
        print(time.process_time() - self.start_time)
        
        for keys in self.warehouse:
            plt.fill(self.warehouse[keys].hullf, self.warehouse[keys].hulld, label=keys, alpha=0.3)
            # plt.plot(self.warehouse[keys].hullf, self.warehouse[keys].hulld, label=keys)
        plt.xlabel('Time (frames)')
        plt.ylabel('Optimal Damage (%)')
        plt.legend(loc='upper left')
        plt.show()
        # plotting
