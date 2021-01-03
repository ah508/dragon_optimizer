Please note: the program recently underwent a rewrite. There's a great deal of
missing documentation, and some of the stuff that used to be possible may not be 
reimplemented.

This is a program designed to find the optimal sequence of actions to take during dragon
form in Dragalia Lost, a mobile title developed by Cygames and published by Nintendo.
Specifically, given an arbitrary, finite time in which to act, we wish to determine a
set of actions (potentially ordered) within that timeframe which will maximize total 
damage dealt by modeling the problem with linear programming.
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

Dependencies:
To run this program, you'll need some additional software installed. Namely,
- Python 3.6+
- numpy
- marshmallow
- python mip
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯

To use the program:
Run template_setup.py before anything else. This is required to generate templates for
the solver to use. If you don't do this, you can't instantiate any solves.

After that, you can test to make sure everything works by running main_solver.py from the 
command line. To run non-test cases, you can either edit the testing dictionary (found in 
main_solver.py) or write your own interface. InputSchema is the format you want to match.
This is pretty jank, but it's also meant to run on a server, not as a standalone application.
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
A. Yes...ish. I do plan to work on this more but I'm running out of free time
    with which to do so.

Q. "What happened to the old optimzier?"
A. I ripped it up. It was bloated, difficult to maintain, and the dependencies were hellish.