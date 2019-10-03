# Copyright (C) 2018 RW Bunney

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.  

# Test workflow class and functions

import unittest

import config as cfg

from classes.workflow import Workflow
from classes.environment import Environment


# TODO Need to test workflow class initialisation on a number of graph types
#  and system specifications.

class TestWorkflowClass(unittest.TestCase):

	def test_add_environment(self):
		wf = Workflow(cfg.test_workflow_data['topcuoglu_graph'])
		env = Environment(cfg.test_workflow_data['topcuoglu_graph_system'])
		retval = wf.add_environment(env)

		# retval = wf.load_attributes('test/data/flop_rep_test.json')

		self.assertEqual(retval, 0)
		self.assertEqual(wf.graph.node[5]['comp'][1], 28)
		self.assertEqual(wf.graph.edges[3, 7]['data_size'], 27)
