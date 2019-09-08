import config

# #####
# def brickWriter(result, zero):
#     print('____________________________________________________')
#     print(f'MOD/s                        |   {result.mps}')
#     print(f'Total Mod                    |   {result.objective}')
#     print(f'Skill Coefficient Breakpoint |   {zero}')
#     print(f'Leniency                     |   {result.leniency} f')
#     print(f'Duration                     |   {result.duration} s')
#     print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
#     print(' ')
# #####

# #####
# def lpWriter(lpOutput, info, zero):
#     print('__________')
#     for i in range(0, len(lpOutput.solution)):
#         if (i < info.rlength-3 and lpOutput.solution[i] != 0 and info.damage[i] != 0) or i >= info.rlength-3:
#             print(f'{info.reference[i]} :  {lpOutput.solution[i]}')
#     print('‾‾‾‾‾‾‾‾‾‾')
#     brickWriter(lpOutput, zero)

# def lpOutput(skill, noskill, info, zero):
#     print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
#     if config.disp_mode == 'Default':
#         print('Default LP')
#         if zero < 1:
#             print('Skill is always Optimal.')
#         if skill.mps >= noskill.mps:
#             lpWriter(skill, info, zero)
#         else:
#             lpWriter(noskill, info, zero)

#     elif config.disp_mode == 'Both':
#         print('Display Both Solutions')
#         lpWriter(skill, info, zero)
#         print('- - - - -')
#         lpWriter(noskill, info, zero)
    
#     elif config.disp_mode == 'Skill':
#         print('Display Skill Only')
#         lpWriter(skill, info, zero)

#     elif config.disp_mode == 'No Skill':
#         print('Display No Skill Only')
#         lpWriter(noskill, info, zero)
# #####

# #####
# def bnbWriter(bnbOutput, info, zero):
#     print('___')
#     for i in bnbOutput.string:
#         if info.reference[i] in ['T  ', 'W  ', 'D  ', 'S  ']:
#             print(f'{info.reference[i]}')
#         else:
#             print(f'{info.reference[i]} ', end=' ')
#     print('\n‾‾‾')
#     brickWriter(bnbOutput, zero)

# def bnbOutput(skill, noskill, info, zero):
#     print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
#     if config.disp_mode == 'Default':
#         print('Default BnB')
#         if zero < 1:
#             print('Skill is always Optimal.')
#         if skill.mps >= noskill.mps:
#             lpWriter(skill, info, zero)
#         else:
#             lpWriter(noskill, info, zero)



class MainDisplay:
    def __init__(self, skill, noskill, info, zero):
        self.skill = skill
        self.noskill = noskill
        self.info = info
        self.zero = zero

    def output(self):
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
        if config.disp_mode == 'Default':
            print('Default Mode')
            if str(self.zero).isnumeric():
                if self.zero < 1:
                    print('Skill is always Optimal.')
            if self.skill.mps >= self.noskill.mps:
                print('> Skill <')
                self.printSwitch(self.skill)
            else:
                print('> No Skill <')
                self.printSwitch(self.noskill)

        elif config.disp_mode == 'Both':
            print('Display Both Solutions')
            print('> Skill <')
            self.printSwitch(self.skill)
            print('- - - - -')
            print('> No Skill <')
            self.printSwitch(self.noskill)
        
        elif config.disp_mode == 'Skill':
            print('Display Skill Only')
            self.printSwitch(self.skill)

        elif config.disp_mode == 'No Skill':
            print('Display No Skill Only')
            self.printSwitch(self.noskill)

    def printSwitch(self, sOutput):
        if sOutput.type == 'LP':
            self.lpWriter(sOutput, self.info)
        elif sOutput.type == 'BnB':
            self.bnbWriter(sOutput, self.info)

    def bnbWriter(self, bnbOutput, info):
        print('___')
        for i in bnbOutput.string:
            if info.reference[i] in ['T  ', 'W  ', 'D  ', 'S  ']:
                print(f'{info.reference[i]}')
            else:
                print(f'{info.reference[i]} ', end=' ')
        print('\n‾‾‾')
        self.brickWriter(bnbOutput)

    def lpWriter(self, lpOutput, info):
        print('__________')
        for i in range(0, len(lpOutput.solution)):
            if (i < info.rlength-3 and lpOutput.solution[i] != 0 and info.damage[i] != 0) or i >= info.rlength-3:
                print(f'{info.reference[i]} :  {lpOutput.solution[i]}')
        print('‾‾‾‾‾‾‾‾‾‾')
        self.brickWriter(lpOutput)

    def brickWriter(self, result):
        print('____________________________________________________')
        print(f'MOD/s                        |   {result.mps}')
        print(f'Total Mod                    |   {result.objective}')
        print(f'Skill Coefficient Breakpoint |   {self.zero}')
        print(f'Leniency                     |   {result.leniency} f')
        print(f'Duration                     |   {result.duration} s')
        print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
        print(' ')

    