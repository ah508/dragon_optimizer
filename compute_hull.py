import config
config.suppress_status = True
config.bnbOverride = False
config.disp_mode = 'Skill'
config.disp_compare = False
config.obj_strat = 'Default'
import time
import main_solver
import matplotlib.pyplot as plt


class HullFinder:
    def __init__(self, dragon, additional_dragons=[]):
        self.dragons = [dragon] + additional_dragons
        self.warehouse = {}

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

        print('Done!')
        print(time.process_time() - main_solver.start_time)
        
        for keys in self.warehouse:
            plt.fill(self.warehouse[keys].hullf, self.warehouse[keys].hulld, label=keys, alpha=0.3)
        plt.xlabel('Time (frames)')
        plt.ylabel('Optimal Damage (%)')
        plt.legend()
        plt.show()


testrun = HullFinder('Agni', ['Cerberus', 'Arctos', 'Sylvia'])
testrun.find_hull()
# config.dragon = dragons[0]
# solution_set_1 = main_solver.Main_Solver()
# solution_set_1.detSolType()
# class Set_1:
#     leaves = []
# for i in range(0, 600):
#     solution_set_1.skill.time = i
#     solution_set_1.solve_problems()
#     Set_1.leaves.append([solution_set_1.skill.objective, i])

# config.dragon = dragons[1]
# solution_set_2 = main_solver.Main_Solver()
# solution_set_2.detSolType()
# class Set_2:
#     leaves = []
# for i in range(0, 600):
#     solution_set_2.skill.time = i
#     solution_set_2.solve_problems()
#     Set_2.leaves.append([solution_set_2.skill.objective, i])
# print('Nearly finished:')
# print(time.process_time() - main_solver.start_time)
# print('-')

# for entity in [Set_1, Set_2]:
#     entity.leafs = sorted(entity.leaves, key=lambda l:l[1])
#     max_damage = -1
#     entity.hulld = []
#     entity.hullf = []
#     for point in entity.leafs:
#         if point[0] > max_damage:
#             entity.hulld.append(point[0])
#             entity.hullf.append(point[1])
#             max_damage = point[0]
#     entity.hullf.append(600)
#     entity.hullf.append(600)
#     entity.hullf.append(0)
#     entity.hulld.append(max(entity.hulld))
#     entity.hulld.append(0)
#     entity.hulld.append(0)

# print('Done!')
# print(time.process_time() - main_solver.start_time)
# plt.fill(Set_1.hullf, Set_1.hulld, "r", Set_2.hullf, Set_2.hulld, "b", alpha=0.3)
# plt.show()