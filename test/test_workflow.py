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

from test import config as cfg

from shadow.models.workflow import Workflow, Task
from shadow.models.environment import Environment
import shadow.algorithms.heuristic as heuristic

# TODO Need to test workflow class initialisation on a number of graph types
#  and system specifications.

current_dir = os.path.abspath('.')


class TestWorkflowSorting(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = Workflow("{0}/{1}".format(current_dir,
                                                  cfg.test_workflow_data[
                                                      'topcuoglu_graph']))

    def test_topological_sort(self):
        task_list = list(self.workflow.sort_tasks("topological"))
        task_order = [t.tid for t in task_list]
        self.assertSequenceEqual([0, 1, 2, 3, 4, 5, 6, 8, 7, 9], task_order)


class TestAddEnvironment(unittest.TestCase):

    def setUp(self):
        self.wf = Workflow("{0}/{1}".format(current_dir, cfg.test_workflow_data[
            'topcuoglu_graph']))
        self.env = Environment("{0}/{1}".format(current_dir,
                                                cfg.test_workflow_data[
                                                    'topcuoglu_graph_system']))

    def test_time_false(self):
        """
        When we read in the environment file and add it to to the workflow,
        we do some pre-processing of the default computing values. If we
        have errors in the workflow or environment config files, we need to
        ensure we exit appropriately.

        We have a workflow with time is false, but time is actually true.
        This means there is more than one value in the 'comp' attribute,
        which is incorrect.

        We have a workflow with time: true, but time is actually false; i.e.
        there is only one value stored in 'comp' attribute, when there
        should be multiply. REMEMBER, time: true implies that runtime
        # has been previously calculated for each machine.
        """

        workflow_true_but_false = Workflow(
            'test/data/workflow/exception_raised_timeistrue.json'
        )
        self.assertRaises(
            TypeError, workflow_true_but_false.add_environment, self.env
        )

    def test_add_environment(self):
        retval = self.wf.add_environment(self.env)
        self.assertEqual(retval, 0)
        for task in self.wf.graph.nodes:
            if task.tid == 5:
                x = [task.calc_runtime(m) for m in self.env.machines]
                self.assertEqual([24, 28, 15], x)

        self.assertEqual(self.wf.graph.edges[Task(3), Task(7)]['data_size'], 27)
