import config
config.suppress_status = True
config.bnbOverride = False
config.disp_compare = False
config.obj_strat = 'Default'
# these need to be set in advance to prevent errors
import time
import main_solver
import matplotlib.pyplot as plt


class HullFinder:
    # computes the 'feasible region' for a dragon wrt time
    # it isn't actually the feasible region, as that is defined by equations of... more than two variables
    # but it is, to some extent, analagous
    # note: this feature isn't really very well developed -
    #   if one of the dragons you want to look at happens to be bufferable, you're gonna have a bad time
    #   like... a real bad time...
    def __init__(self, dragon, additional_dragons=[]):
        self.dragons = [dragon] + additional_dragons
        self.warehouse = {}
        # warehouse is a terrible variable name

    class Storage:
        def __init__(self):
            self.leaves = []

    def find_hull(self):
        for creature in self.dragons:
            config.dragon = creature
            self.warehouse[creature] = self.Storage()
            self.warehouse[creature].solution_set = main_solver.Main_Solver()
            self.warehouse[creature].solution_set.detSolType()
            for i in range(0, 600):
                self.warehouse[creature].solution_set.skill.time = i
                self.warehouse[creature].solution_set.solve_problems()
                self.warehouse[creature].leaves.append([self.warehouse[creature].solution_set.skill.objective, i])
            # finding the optimal solution for every time moment between 0 and 600
            # this is a terrible way to handle this BUT - it works for now.
            # I'll find some way to make it smoother later
            print('Segment')
            print(time.process_time() - main_solver.start_time)
            print('-')
        
        for entity in self.warehouse.values():
            entity.leafs = sorted(entity.leaves, key=lambda l:l[1])
            max_damage = -1
            entity.hulld = []
            entity.hullf = []
            for point in entity.leafs:
                if point[0] > max_damage:
                    entity.hulld.append(point[0])
                    entity.hullf.append(point[1])
                    max_damage = point[0]
            entity.hullf.append(600)
            entity.hullf.append(600)
            entity.hullf.append(0)
            entity.hulld.append(max(entity.hulld))
            entity.hulld.append(0)
            entity.hulld.append(0)
            # determining the vertices - this is what lets us display the polygon below

        print('Done!')
        print(time.process_time() - main_solver.start_time)
        
        for keys in self.warehouse:
            plt.fill(self.warehouse[keys].hullf, self.warehouse[keys].hulld, label=keys, alpha=0.3)
        plt.xlabel('Time (frames)')
        plt.ylabel('Optimal Damage (%)')
        plt.legend(loc='upper left')
        plt.show()
        # plotting
