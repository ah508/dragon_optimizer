import config
import scipy.optimize as spOpt

def find_zero(x, string1, string2):
    """A function used for Newton's rootfinding method
    
    Compares the results of two solution methods to determine which is
    more 'efficient.' It is used exclusively as a helper function for
    rootfinding. 

    Parameters
    ----------
    x : float
        A skill coefficient, independent of that specified in
        config.
    string1 : class instance
        A solved instance of either LPsolution, SLPsolution, or
        BnBsolution.
    string2 : class instance
        A solved instance of either LPsolution, SLPsolution, or
        BnBsolution.
    
    Returns
    -------
    difference : float
        The difference in damage per second of the compared
        methods.
    """

    comboDPS = []
    for combo in [string1, string2]:
        if combo.use_skill:
            comboDPS += [(x*combo.damage[-1]/config.skill_coefficient + combo.objective - combo.damage[-1])/(combo.duration)]
        else:
            comboDPS += [combo.objective/combo.duration]
    difference = comboDPS[0] - comboDPS[1]
    return difference
    # If skill is used, it needs to correct for the skill coefficient
    # in config.  Can (and should) be simplified a bit further, mps is
    # already computed.

def root_find(string1, string2):
    """Finds the skill coefficient breakpoint of two solution methods.

    Uses Newton's rootfinding method to determine the skill coefficient
    at which two different solution methods produce equivalent damage
    per second. If the skill does not do damage, then there will not
    be a zero, and so the value is either positive or negative infinity
    depending on the initial results.
    
    With the current implementation, it is possible (and probable, in
    the case of transformation canceling) to produce impossible values,
    or values that do not make sense. This was deemed a necessary
    concession.

    Parameters
    ----------
    string1 : class instance
        A solved instance of either LPsolution, SLPsolution, or
        BnBsolution.
    string2 : class instance
        A solved instance of either LPsolution, SLPsolution, or
        BnBsolution.
        
    Returns
    -------
    float
        The skill coefficient at which the two solution methods
        produce equivalent damage per second.
    """

    if string1.damage[-1] != 0:
        zero = round(spOpt.newton(find_zero, 1, args=(string1, string2)), 3)
    elif string1.objective >= string2.objective: 
        zero = '-Inf'
    elif string1.objective < string2.objective:
        zero = 'Inf'
    return zero