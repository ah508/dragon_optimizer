import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/ubuntu/testrepo/proj/dragon_optimizer")

from api import app as application
