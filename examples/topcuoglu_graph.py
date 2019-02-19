# import config as cfg

from algorithms.heuristic import heft
from classes.workflow import Workflow

# This workflow calculates the task time for each resource based on the demand and supply vectors provided in the 'flop_rep_test.json' file. 
wf = Workflow('topcuoglu.graphml')
retval = wf.load_attributes('flop_rep_test.json')
print(heft(wf))
wf.pretty_print_allocation()


# Original HEFT workflow; task time on reach resource is provided directly by the .json file. 
wf = Workflow('topcuoglu.graphml')
retval = wf.load_attributes('heft.json',calc_time=False)
print(heft(wf))
wf.pretty_print_allocation()