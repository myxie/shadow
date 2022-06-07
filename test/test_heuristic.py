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

########################################################################
import unittest
import networkx as nx
import os
import logging

from test import config as cfg
from shadow.algorithms.heuristic import heft, pheft, \
    fcfs, generate_ranking_matrix, \
    calculate_upward_ranks
from shadow.models.workflow import Workflow, Task
from shadow.models.environment import Environment
from shadow.models.solution import Solution, Allocation

# CHANGE THIS TO GET DEBUG VALUES FROM LOGS
# logging.basicConfig(level='WARNING')
# Tests for /algorithms/heuristic.py


# Testing heft algorithms in heuristics.py 

current_dir = os.path.abspath('.')


class TestFCFS(unittest.TestCase):

    def setUp(self):
        self.workflow = Workflow("{0}/{1}".format(current_dir,
                                                  cfg.test_heuristic_data[
                                                      'topcuoglu_graph']))
        self.env = Environment("{0}/{1}".format(current_dir,
                                                cfg.test_workflow_data[
                                                    'topcuoglu_graph_system']))
        self.workflow.add_environment(self.env)

    def test_fcfs_allocations(self):
        # The order should be [0, 5, 4, 3, 2, 6, 1, 8, 7, 9]
        solution = fcfs(workflow=self.workflow)
        for t in self.workflow.tasks:
            if t.tid == 0:
                alloc = solution.task_allocations[t]
                self.assertEqual(0, alloc.ast)
                # self.assertEqual(11, alloc.aft)
            if t.tid == 4:
                continue
        self.assertEqual(112,solution.makespan)


# if all(k in task_ranks for k in succs):


class TestHeftMethods(unittest.TestCase):
    """
    This class test HEFT on the same example graph presented by
    Topcuoglu et al
    """

    def setUp(self):
        self.workflow = Workflow("{0}/{1}".format(current_dir,
                                                  cfg.test_heuristic_data[
                                                      'topcuoglu_graph_nocalc']))
        env = Environment("{0}/{1}".format(current_dir, cfg.test_workflow_data[
            'topcuoglu_graph_system']))
        self.workflow.add_environment(env)

    # self.workflow.load_attributes(cfg.test_heuristic_data['heft_attr'],calc_time=False)

    def test_rank(self):
        rank_values = [108, 77, 79, 80, 69, 63, 42, 35, 44, 14]
        # for task in self.workflow.tasks:
        # 	task.rank = rank_up(self.workflow, task)
        task_ranks = calculate_upward_ranks(self.workflow)
        # upward_rank(self.workflow)
        for task in self.workflow.tasks:
            task.rank = task_ranks[task]
        sorted_tasks = self.workflow.sort_tasks('rank')

        for node in sorted_tasks:
            self.assertTrue(rank_values[node.tid] == int(node.rank))

    def test_schedule(self):
        solution = heft(self.workflow)
        self.assertEqual(80, solution.makespan)


class TestHeftMethodCalcTime(unittest.TestCase):
    def setUp(self):
        self.workflow = Workflow(
            f"{current_dir}/{cfg.test_workflow_data['topcuoglu_graph']}"
        )
        env = Environment("{0}/{1}".format(current_dir, cfg.test_workflow_data[
            'topcuoglu_graph_system']))

        # self.workflow = Workfow(cfg.test_heuristic_data['topcuoglu_graph'],
        # cfg.test_heuristic_data['topcuoglu_graph_system'])

        self.workflow.add_environment(env)

    # self.workflow.load_attributes(cfg.test_heuristic_data['flops_test_attr'])

    def test_schedule(self):
        solution = heft(self.workflow)
        self.assertEqual(98, solution.makespan)


@unittest.SkipTest
class TestHeftMethodLargeGraph(unittest.TestCase):

    def test_large_workflow(self):
        self.workflow = Workflow(
            "test/data/heuristic/hpso01_time-18000_channels-512_tel"
            "-512_no_data"
            ".json"
        )
        env = Environment(
            "test/data/heuristic/shadow_low_sdp_config.json"
        )
        self.workflow.add_environment(env)
        solution = heft(self.workflow)
        print(solution.makespan)


class TestPHeftMethods(unittest.TestCase):

    def setUp(self):
        self.workflow = Workflow(cfg.test_heuristic_data['pheft_graph'])
        env = Environment(cfg.test_workflow_data['topcuoglu_graph_system'])
        self.workflow.add_environment(env)
        self.up_oct_rank_values = [72, 41, 37, 43, 31, 41, 17, 20, 16, 0]
        self.up_rank_values = [169, 114, 102, 110, 129, 119, 52, 92, 42, 20]

    def tearDown(self):
        return -1

    def test_up_rank(self):
        task_ranks = calculate_upward_ranks(self.workflow)
        # upward_rank(self.workflow)
        for task in self.workflow.tasks:
            task.rank = task_ranks[task]
        sorted_tasks = self.workflow.sort_tasks('rank')
        for node in sorted_tasks:
            self.assertTrue(int(node.rank) ==
                            self.up_rank_values[node.tid])

    def test_oct_rank(self):
        oct_rank_matrix = generate_ranking_matrix(self.workflow)
        # upward_oct_rank(self.workflow, oct_rank_matrix)
        for task in self.workflow.tasks:
            sum = 0
            for (t, p) in oct_rank_matrix:
                if t is task:
                    sum += oct_rank_matrix[(t, p)]

            rank = int(sum / len(self.workflow.env.machines))
            task.rank = rank

        sorted_tasks = self.workflow.sort_tasks('rank')

        for node in sorted_tasks:
            self.assertEqual(self.up_oct_rank_values[node.tid],
                             node.rank)

    def test_heft_schedule(self):
        # upward_rank(self.workflow)
        solution = heft(self.workflow)
        self.assertTrue(solution.makespan == 133)

    def test_pheft_schedule(self):
        # upward_rank(self.workflow)
        solution = pheft(self.workflow)
        self.assertTrue(solution.makespan == 122)


@unittest.SkipTest
class TestDALiuGEGraph(unittest.TestCase):

    def setUp(self):
        self.workflow = Workflow('test/data/daliugesample.json',
                                 cfg.test_heuristic_data[
                                     'topcuoglu_graph_system'],
                                 calc_time=False)
        self.dense = Workflow('test/data/ggen_out_4-denselu.json',
                              cfg.test_heuristic_data['topcuoglu_graph_system'],
                              calc_time=False)
        self.gnp = Workflow('test/data/ggen_out_20-0.5.json',
                            cfg.test_heuristic_data['topcuoglu_graph_system'],
                            calc_time=False)

    def tearDown(self):
        pass

    def test_it_works(self):
        print(heft(self.dense))
        self.dense.pretty_print_allocation()

        pass
