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
                self.print_switch(self.skill)
            elif max_MPS == self.noskill.mps:
                print('> No Skill <')
                self.print_switch(self.noskill)
            elif max_MPS == self.tcancel.mps:
                print('> Transform Cancel <')
                self.print_switch(self.tcancel)
        
        else:
            if 'skill' in config.disp_mode:
                print('> Skill <')
                self.print_switch(self.skill)

            if 'noskill' in config.disp_mode:
                print('> No Skill <')
                self.print_switch(self.noskill)

            if 'tcancel' in config.disp_mode:
                print('> Transform Cancel <')
                self.print_switch(self.tcancel)

    def print_switch(self, solved_output):
        """Determines which output method is suitible.

        Parameters
        ----------
        solved_output : class instance
            A solved instance of either BnBsolution, LPsolution,
            or SLPsolution.

        Returns
        -------
        None.
        """
        if solved_output.type == 'LP':
            self.lp_writer(solved_output)
        elif solved_output.type == 'BnB':
            self.bnb_writer(solved_output)
        elif solved_output.type == 'SLP':
            self.slp_writer(solved_output)

    def bnb_writer(self, bnb_output):
        """Prints output for a branch and bound problem.
        
        Parameters
        ----------
        bnb_output : class instance
            A solved instance of BnBsolution.
            
        Returns
        -------
        None. Output is printed.
        """

        print('___')
        for i in bnb_output.string:
            if bnb_output.reference[i] in ['T  ', 'W  ', 'D  ', 'S  ']:
                print(f'{bnb_output.reference[i]}')
            else:
                print(f'{bnb_output.reference[i]} ', end=' ')
        print('\n‾‾‾')
        self.brick_writer(bnb_output)

    def lp_writer(self, lp_output):
        """Prints output for a linear programming problem.
        
        Parameters
        ----------
        lp_output : class instance
            A solved instance of LPsolution.
            
        Returns
        -------
        None. Output is printed.
        """

        print('__________')
        for i in range(0, len(lp_output.solution)):
            if (i < lp_output.rlength-3 and lp_output.solution[i] != 0 and lp_output.damage[i] != 0) or i >= lp_output.rlength-3:
                print(f'{lp_output.reference[i]} :  {lp_output.solution[i]}')
        print('‾‾‾‾‾‾‾‾‾‾')
        self.brick_writer(lp_output)

    def slp_writer(self, slp_output):
        """Prints output for a separable linear programming problem.
        
        Parameters
        ----------
        slp_output : class instance
            A solved instance of SLPsolution.
            
        Returns
        -------
        None. Output is printed
        """

        totals = slp_output.solution[0:2]
        unboosted = slp_output.solution[2:slp_output.rlength+1]
        boosted = slp_output.solution[slp_output.rlength+1:2*slp_output.rlength]
        exit_vars = slp_output.solution[2*slp_output.rlength:]
        print('Unboosted           Boosted')
        print('_____________        _____________')
        print('M   : %6.2f        M   : %6.2f' %(totals[0], totals[1]))
        for i in range(0, len(unboosted)):
            print(f'{slp_output.reference[i]} : {unboosted[i]}            {slp_output.reference[i+1]} : {boosted[i]}')
        print('‾‾‾‾‾‾‾‾‾‾‾‾‾        ‾‾‾‾‾‾‾‾‾‾‾‾‾')
        for i in range(0, len(exit_vars)):
            if exit_vars[i] != 0:
                print(f'Exit Variable: {slp_output.reference[i+2]}')
        self.brick_writer(slp_output)

    def brick_writer(self, result):
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

    