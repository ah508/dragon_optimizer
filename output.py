import config

class MainDisplay:
    def __init__(self, skill, noskill, tcancel, info, zero):
        self.skill = skill
        self.noskill = noskill
        self.tcancel = tcancel
        self.info = info
        self.zero = zero

    def output(self):
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
        if config.disp_mode == 'Default':
            print('Default Mode')
            try:
                if self.zero[0] < 1 or self.zero[1] < 1:
                    print('Skill > No Skill.')
                if self.zero[1] <= self.zero[0]:
                    print('Transform Cancel is Favorable.')
            except TypeError:
                pass
            max_MPS = max([self.skill.mps, self.noskill.mps, self.tcancel.mps])
            if max_MPS == self.skill.mps: 
                print('> Skill <')
                self.printSwitch(self.skill)
            elif max_MPS == self.noskill.mps:
                print('> No Skill <')
                self.printSwitch(self.noskill)
            elif max_MPS == self.tcancel.mps:
                print('> Transform Cancel <')
                self.printSwitch(self.tcancel)
                

        elif config.disp_mode == 'Full List':
            print('Display All Solutions')
            print('> Skill <')
            self.printSwitch(self.skill)
            print('- - - - -')
            print('> No Skill <')
            self.printSwitch(self.noskill)
            print('- - - - -')
            print('> Transform Cancel <')
            self.printSwitch(self.tcancel)
        
        elif config.disp_mode == 'Skill':
            print('Display Skill Only')
            self.printSwitch(self.skill)

        elif config.disp_mode == 'No Skill':
            print('Display No Skill Only')
            self.printSwitch(self.noskill)

        elif config.disp_mode == 'Transform Cancel':
            print('Display Transform Cancel Only')
            self.printSwitch(self.tcancel)

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
        print('____________________________________________________________')
        print(f'MOD/s                                  |   {result.mps}')
        print(f'Total Mod                              |   {result.objective}')
        print(f'Skill ~ No Skill Breakpoint            |   {self.zero[0]}')
        print(f'Transform Cancel ~ No Skill Breakpoint |   {self.zero[1]}')
        print(f'Transform Cancel ~ Skill Breakpoint    |   {self.zero[2]}')
        print(f'Leniency                               |   {result.leniency} f')
        print(f'Duration                               |   {result.duration} s')
        print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
        print(' ')

    