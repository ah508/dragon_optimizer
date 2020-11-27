Please note: the program is undergoing a rewrite at the moment. There's a great deal of
missing data, and even more missing documentation, and some of the stuff that used to
be possible may not be reimplemented yet, or may not be planned for reimplementation.

This is a program designed to find the optimal sequence of actions to take during dragon
form in Dragalia Lost, a mobile title developed by Cygames and published by Nintendo.
Specifically, given an arbitrary, finite time in which to act, we wish to determine a
set of actions (potentially ordered) within that timeframe which will maximize either:
    a) Total Damage Dealt (in %)
    b) Damage Dealt per Second (in %)

(a) is achieved by modeling the situation as a Linear Programming Problem (LPP) and
using an existing solver to determine the optimum value. (b) is achieved by solving for
(a) in two cases, and then selecting the case with the higher dps.
Note: this hasn't yet been reimplemented.
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

Dependencies:
To run this program, you'll need some additional software installed. Namely,
- Python 3.6+
- numpy
- python mip
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

To use the program:
Run main_solver.py from the command line. To change the chosen dragon or
selected settings, you'll need to modify the testing dictionary (also found
in main_solver). This is jankier than the previous version. It will get better,
just give me a bit of time.
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

FAQ (probably)

Q. "What's with the awful dependency list?"
A. Hey, I think it's quite reasonable this time, you should have seen it before!

Q. "Why isn't there any documentation?"
A. Great question - I'm getting to it.

Q. "Is it possible to do all of this by dynamic programming?"
A. Yep. It's hard to say whether or not that would be a better approach. Linear
    programming is pretty darn fast, even with mip's overhead. DP would definitely
    be more flexible, at least. I would encourage you to give it a shot if you
    have any interest - such a solver is not in my future plans.

Q. "Are there plans to make this program more comprehensive?"
A. Yes.

Q. "I see that in the sheet, some attacks that are two hits are listed as just one 
    single hit. What's up with that?"
A. In those cases, the attack in question is a proper projectile. If the first hit would
    occur, the second hit follows inevitably. You would be correct to call out that this
    introduces inaccuracies both with buff handling and at the end of dragon time, but 
    accurately modeling stuff like that is... difficult with the current approach.