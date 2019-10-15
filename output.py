import config

class MainDisplay:
    """Formats and prints output.

    Parameters
    ----------
    skill : class instance
        A solved instance of either LPsolution, SLPsolution, or
        BnBsolution.
    noskill : class instance
        A solved instance of either LPsolution, SLPsolution, or
        BnBsolution.
    tcancel : class instance
        A solved instance of either LPsolution, SLPsolution, or
        BnBsolution.
    zero : [float] or [str]
        A vector of breakpoints between the three solutions. If
        one or more of the three problems was not solved, then
        that cell contains 'Not Computed.'
    """
    def __init__(self, skill, noskill, tcancel, zero):
        self.skill = skill
        self.noskill = noskill
        self.tcancel = tcancel
        self.zero = zero

    def output(self):
        """Determines the basic mode of output.
        
        Parameters
        ----------
        None. This method uses attributes of the class.

        Returns
        -------
        None.
        """

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
        
        else:
            if 'skill' in config.disp_mode:
                print('> Skill <')
                self.printSwitch(self.skill)

            if 'noskill' in config.disp_mode:
                print('> No Skill <')
                self.printSwitch(self.noskill)

            if 'tcancel' in config.disp_mode:
                print('> Transform Cancel <')
                self.printSwitch(self.tcancel)

    def printSwitch(self, sOutput):
        """Determines which output method is suitible.

        Parameters
        ----------
        sOutput : class instance
            A solved instance of either BnBsolution, LPsolution,
            or SLPsolution.

        Returns
        -------
        None.
        """
        if sOutput.type == 'LP':
            self.lpWriter(sOutput)
        elif sOutput.type == 'BnB':
            self.bnbWriter(sOutput)
        elif sOutput.type == 'SLP':
            self.slpWriter(sOutput)

    def bnbWriter(self, bnbOutput):
        """Prints output for a branch and bound problem.
        
        Parameters
        ----------
        bnbOutput : class instance
            A solved instance of BnBsolution.
            
        Returns
        -------
        None. Output is printed.
        """

        print('___')
        for i in bnbOutput.string:
            if bnbOutput.reference[i] in ['T  ', 'W  ', 'D  ', 'S  ']:
                print(f'{bnbOutput.reference[i]}')
            else:
                print(f'{bnbOutput.reference[i]} ', end=' ')
        print('\n‾‾‾')
        self.brickWriter(bnbOutput)

    def lpWriter(self, lpOutput):
        """Prints output for a linear programming problem.
        
        Parameters
        ----------
        lpOutput : class instance
            A solved instance of LPsolution.
            
        Returns
        -------
        None. Output is printed.
        """

        print('__________')
        for i in range(0, len(lpOutput.solution)):
            if (i < lpOutput.rlength-3 and lpOutput.solution[i] != 0 and lpOutput.damage[i] != 0) or i >= lpOutput.rlength-3:
                print(f'{lpOutput.reference[i]} :  {lpOutput.solution[i]}')
        print('‾‾‾‾‾‾‾‾‾‾')
        self.brickWriter(lpOutput)

    def slpWriter(self, slpOutput):
        """Prints output for a separable linear programming problem.
        
        Parameters
        ----------
        slpOutput : class instance
            A solved instance of SLPsolution.
            
        Returns
        -------
        None. Output is printed
        """

        totals = slpOutput.solution[0:2]
        unboosted = slpOutput.solution[2:slpOutput.rlength+1]
        boosted = slpOutput.solution[slpOutput.rlength+1:2*slpOutput.rlength]
        exitVars = slpOutput.solution[2*slpOutput.rlength:]
        print('Unboosted           Boosted')
        print('_____________        _____________')
        print('M   : %6.2f        M   : %6.2f' %(totals[0], totals[1]))
        for i in range(0, len(unboosted)):
            print(f'{slpOutput.reference[i]} : {unboosted[i]}            {slpOutput.reference[i+1]} : {boosted[i]}')
        print('‾‾‾‾‾‾‾‾‾‾‾‾‾        ‾‾‾‾‾‾‾‾‾‾‾‾‾')
        for i in range(0, len(exitVars)):
            if exitVars[i] != 0:
                print(f'Exit Variable: {slpOutput.reference[i+2]}')
        self.brickWriter(slpOutput)

    def brickWriter(self, result):
        """Prints general output for a chosen solution.
        
        Parameters
        ----------
        result : class instance
            A solved instance of either BnBsolution, LPsolution,
            or SLPsolution.
            
        Returns
        -------
        None. Output is printed.
        """

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

    