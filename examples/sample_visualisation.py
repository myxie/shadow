from shadow.algorithms.heuristic import heft

from shadow.models.workflow import Workflow, Task
from shadow.models.environment import Environment

from shadow.visualiser.visualiser import AllocationPlot
from test import config

HEFTWorkflow = Workflow(config.test_heuristic_data['topcuoglu_graph'])
env = Environment(config.test_heuristic_data['topcuoglu_graph_system'])
HEFTWorkflow.add_environment(env)
heft(HEFTWorkflow)

sample_allocation = AllocationPlot(solution=HEFTWorkflow.solution)
sample_allocation.plot()
