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
import os

import test_config as cfg

from shadow.classes.workflow import Workflow
from shadow.classes.environment import Environment


# TODO Need to test workflow class initialisation on a number of graph types
#  and system specifications.

current_dir = os.path.abspath('.')
class TestWorkflowClass(unittest.TestCase):

	def test_add_environment(self):
		wf = Workflow("{0}/{1}".format(current_dir, cfg.test_workflow_data['topcuoglu_graph']))
		env = Environment("{0}/{1}".format(current_dir,cfg.test_workflow_data['topcuoglu_graph_system']))
		retval = wf.add_environment(env)

		# retval = wf.load_attributes('test/data/flop_rep_test.json')

		self.assertEqual(retval, 0)
		self.assertEqual(28, wf.graph.nodes[5]['comp'][1])
		self.assertEqual(wf.graph.edges[3, 7]['data_size'], 27)
