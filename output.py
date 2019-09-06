import config

def brickWriter(result, zero):
    print('____________________________________________________')
    print(f'MOD/s                        |   {result.mps}')
    print(f'Total Mod                    |   {result.objective}')
    print(f'Skill Coefficient Breakpoint |   {zero}')
    print(f'Leniency                     |   {result.leniency} f')
    print(f'Duration                     |   {result.duration} s')
    print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
    print(' ')


def lpWriter(lpOutput, info, zero):
    print('__________')
    for i in range(0, len(lpOutput.solution)):
        if (i < info.rlength-3 and lpOutput.solution[i] != 0 and info.damage[i] != 0) or i >= info.rlength-3:
            print(f'{info.reference[i]} :  {lpOutput.solution[i]}')
    print('‾‾‾‾‾‾‾‾‾‾')
    brickWriter(lpOutput, zero)

def lpOutput(skill, noskill, info, zero):
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
    if config.disp_mode == 'Default':
        print('Default Mode')
        if zero < 1:
            print('Skill is always Optimal.')
        if skill.mps >= noskill.mps:
            lpWriter(skill, info, zero)
        else:
            lpWriter(noskill, info, zero)

    elif config.disp_mode == 'Both':
        print('Display Both Solutions')
        lpWriter(skill, info, zero)
        print('- - - - -')
        lpWriter(noskill, info, zero)
    
    elif config.disp_mode == 'Skill':
        print('Display Skill Only')
        lpWriter(skill, info, zero)

    elif config.disp_mode == 'No Skill':
        print('Display No Skill Only')
        lpWriter(noskill, info, zero)


        
