This is a program designed to find the optimal sequence of actions to take during dragon
form in Dragalia Lost, a mobile title developed by Cygames and published by Nintendo.
Specifically, given an arbitrary, finite time in which to act, we wish to determine a
set of actions (potentially ordered) within that timeframe which will maximize either:
    a) Total Damage Dealt (in %)
    b) Damage Dealt per Second (in %)

(a) is achieved by modeling the situation as a Linear Programming Problem (LPP) and
using an existing solver to determine the optimum value. (b) is achieved by solving for
(a) in three cases, and then selecting the case with the maximum mod/s value.
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

Dependencies:
To run this program, you'll need some additional software installed. Namely,
- A relatively up-to-date version of R
- The lpSolve package for R
- Python 3.6+
- pybnb (This may require you to have mpi4py installed. If you can't get that to work
        for some reason, you can disable it in pybnb)
- numpy
- pandas
- scipy
- rpy2
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

To use the program:
Run optimize_drag.py [dragon] from the command line, where argument [dragon] is the name
of the dragon you wish to optimize. (note, this is case sensitve)
For example, if I wanted to find Agni's optimal combo, I would call:
    python optimize_drag.py Agni
To learn more about the other arguments you can use, run with argument -h
    python optimize_drag.py -h
To change the default settings, you can edit config.py directly.
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

FAQ (probably)

Q. "What's with the awful dependency list?"
A. Good question.

Q. "If you're going to pass to an R instance anyway, why didn't you write the whole
    thing in R?"
A. Originally, it was all written in R. The project was moved to python because it
    made it easier to implement alternative solution methods, like branch and bound.
    Additionally, if I ever move to dedicated optimization software (like CPLEX) it
    will be easier to jump between python and [software] than R and [software].

Q. "Alright, then why are you passing to R in the first place? Doesn't python have
    libraries to handle LPs?"
A. Comfort, mostly. I also wanted to learn how to use rpy2. If this ever gets rewritten
    (again) that dependency may be removed in favor of something more accessible.

Q. "Why are you using branch and bound? Can't you do it all by LP?"
A. Yes, it is possible to solve all (or at least almost all) of the current problems
    with linear programming. Unfortunately, doing so would also constitute a great
    deal of work. Someday, maybe, that work will get done, but for now I don't really
    have the time. As a result, the bnb won't be going anywhere for a while.

Q. "Is it possible to do all of this by dynamic programming?"
A. Yep. In certain cases, (those that use enumerative methods) DP would be far superior.
    Personally, I don't have much experience with dynamic programming though, so it's
    going on the to do list.

Q. "This doesn't have the dragon I want to work with, what do?"
A. You may not have an up-to-date version of the csv. You can grab one from the Discrete
    Framedata tab of the Optimization Mastersheet, located here:
    https://docs.google.com/spreadsheets/d/1k-CROHAKTOGvR7-gJG5kFdMOc_qP5KayJ46fEI58GHI/edit?usp=sharing
    
    If that still doesn't have what you need, you can try hunting me down on the
    DL subreddit discord.

Q. "Are there plans to make this program more comprehensive?"
A. Yeah, but I really only work on this in my spare time, so don't expect frequent 
    updates or anything.

Q. "I see that in the sheet, some attacks that are two hits are listed as just one 
    single hit. What's up with that?"
A. In those cases, the attack in question is a proper projectile. If the first hit would
    occur, the second hit follows inevitably. You would be correct to call out that this
    introduces inaccuracies with buff handling and the end of dragon time, but 
    unfortunately we have no way to account for the potential variability in the timing 
    of those two hits. Regrettably, this is a concession we just have to make, as
    seperating the entries increases the computational burden with no real benefit.