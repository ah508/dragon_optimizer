This is a program designed to find the optimal sequence of actions to take during dragon
form in Dragalia Lost, a mobile title developed by Cygames and published by Nintendo.

Specifically, given an arbitrary, finite time in which to act, we wish to determine a
set of actions (potentially ordered) within that timeframe which will maximize total 
damage dealt by modeling the problem with linear programming.

Please note: the program recently underwent a rewrite. There's a great deal of
missing documentation, and some of the stuff that used to be possible may not be 
reimplemented.

## Dependencies
To run this program, you'll need some additional software installed. Namely,
- Python 3.6+
- numpy
- marshmallow
- [python mip](https://python-mip.readthedocs.io/en/latest/)

These are all in **requirements.txt**

## Using the program
Before anything else, run **template_setup.py** (you may need to manually add a folder or two). 
This is required to generate templates for the solver to use. 
If you don't do this, you can't instantiate any solves.

After that, you can test to make sure everything works by running **main_solver.py** from the 
command line. To run non-test cases, you can either edit the testing dictionary (found in 
main_solver.py) or write your own interface. InputSchema is the format you want to match.
This is pretty jank, but it's also meant to run on a server, not as a standalone application.

## FAQ (probably)
#### "Is it possible to do all of this by dynamic programming?"
Yep. It's hard to say whether or not that would be a better approach. Linear
programming is pretty darn fast, even with mip's overhead. DP would definitely
be more flexible, at least. I would encourage you to give it a shot if you
have any interest - such a solver is not in my future plans.

#### "Are there plans to make this program more comprehensive?"
Yes...ish. I do plan to work on this more but I'm running out of free time
with which to do so.

#### "What happened to the old optimzier?"
I ripped it up. It was bloated, difficult to maintain, and the dependencies were hellish.

#### "What about the old spreadsheet?"
It's [still available](https://docs.google.com/spreadsheets/d/1k-CROHAKTOGvR7-gJG5kFdMOc_qP5KayJ46fEI58GHI/edit?usp=sharing)
but I am no longer updating it. If I ever get around to adding verifications to the site, I intend to take it down for good.
    
#### "Where's the frontend?"
It's [in a different repo](https://github.com/ah508/dragon_optimizer_frontend).
