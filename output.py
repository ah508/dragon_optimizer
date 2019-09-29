import config

class MainDisplay:
    # just a simple means of output
    # I don't think there's really much here that needs explanation
    def __init__(self, skill, noskill, tcancel, zero):
        self.skill = skill
        self.noskill = noskill
        self.tcancel = tcancel
        self.zero = zero

    def output(self):
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(config.dragon)
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
            self.lpWriter(sOutput)
        elif sOutput.type == 'BnB':
            self.bnbWriter(sOutput)
        elif sOutput.type == 'SLP':
            self.slpWriter(sOutput)

    def bnbWriter(self, bnbOutput):
        print('___')
        for i in bnbOutput.string:
            if bnbOutput.reference[i] in ['T  ', 'W  ', 'D  ', 'S  ']:
                print(f'{bnbOutput.reference[i]}')
            else:
                print(f'{bnbOutput.reference[i]} ', end=' ')
        print('\n‾‾‾')
        self.brickWriter(bnbOutput)

    def lpWriter(self, lpOutput):
        print('__________')
        for i in range(0, len(lpOutput.solution)):
            if (i < lpOutput.rlength-3 and lpOutput.solution[i] != 0 and lpOutput.damage[i] != 0) or i >= lpOutput.rlength-3:
                print(f'{lpOutput.reference[i]} :  {lpOutput.solution[i]}')
        print('‾‾‾‾‾‾‾‾‾‾')
        self.brickWriter(lpOutput)

    def slpWriter(self, slpOutput):
        tots = slpOutput.solution[0:2]
        unboosted = slpOutput.solution[2:slpOutput.rlength+1]
        boosted = slpOutput.solution[slpOutput.rlength+1:2*slpOutput.rlength]
        exitVars = slpOutput.solution[2*slpOutput.rlength:]
        print('Unboosted           Boosted')
        print('_____________        _____________')
        print('M   : %6.2f        M   : %6.2f' %(tots[0], tots[1]))
        for i in range(0, len(unboosted)):
            print(f'{slpOutput.reference[i]} : {unboosted[i]}            {slpOutput.reference[i+1]} : {boosted[i]}')
        print('‾‾‾‾‾‾‾‾‾‾‾‾‾        ‾‾‾‾‾‾‾‾‾‾‾‾‾')
        for i in range(0, len(exitVars)):
            if exitVars[i] != 0:
                print(f'Exit Variable: {slpOutput.reference[i+2]}')
        self.brickWriter(slpOutput)

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

    