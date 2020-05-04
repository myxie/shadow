from queue import Queue
from shadow.algorithms.heuristic import heft

from shadow.models.workflow import Workflow, Task
from shadow.models.environment import Environment

HEFTWorkflow = Workflow('heft.json')
env = Environment('sys.json')
HEFTWorkflow.add_environment(env)

print(heft(HEFTWorkflow))

DelayWorkflow = Workflow('heft_delay.json')
DelayWorkflow.add_environment(env)
print(heft(DelayWorkflow))


def calc_task_delay(task, delay, workflow):
	t = workflow.graph.tasks[task]
	aft = t.aft
	update_list = list(workflow.graph.successors(t))
	# add 10 to the start and finish time of each of these successors, and their successors
	update_queue = Queue()
	update_queue.put(update_list)
	print(update_queue)
	return workflow

task = HEFTWorkflow.tasks[0]
calc_task_delay(task, 10, workflow=HEFTWorkflow)
