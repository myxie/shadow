import unittest
import os

from test import config as cfg

from shadow.models.workflow import Workflow
from shadow.models.environment import Environment

from shadow.algorithms.heuristic import heft

current_dir = os.path.abspath('.')


class TestWorkflowClass(unittest.TestCase):

	def setUp(self):
		self.workflow = Workflow("{0}/{1}".format(current_dir, cfg.test_workflow_data['topcuoglu_graph']))
		self.env = Environment("{0}/{1}".format(current_dir, cfg.test_workflow_data['topcuoglu_graph_system']))
		self.workflow.add_environment(self.env)

	def test_execution_order(self):
		correct_order = [0, 3, 2, 4, 1, 5, 6, 8, 7, 9]
		retval = heft(self.workflow)
		order = self.workflow.solution.execution_order
		for i, alloc in enumerate(order):
			self.assertEqual(correct_order[i], alloc.tid)

