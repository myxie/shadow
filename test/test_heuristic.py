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

import config as cfg
from algorithms.heuristic import upward_rank, upward_oct_rank, \
	sort_tasks, heft, pheft
from classes.workflow import Workflow
from classes.environment import Environment


# Tests for /algorithms/heuristic.py


# Testing heft algorithms in heuristics.py 

class TestHeftMethods(unittest.TestCase):
	"""
	This class test HEFT on the same example graph presented by
	Topcuoglu et al
	"""

	def setUp(self):
		self.wf = Workflow(cfg.test_heuristic_data['topcuoglu_graph_nocalc'])
		env = Environment(cfg.test_workflow_data['topcuoglu_graph_system'])
		self.wf.add_environment(env)

	# self.wf.load_attributes(cfg.test_heuristic_data['heft_attr'],calc_time=False)

	def test_rank(self):
		rank_values = [108, 77, 79, 80, 69, 63, 42, 35, 44, 14]
		upward_rank(self.wf)
		sorted_tasks = sort_tasks(self.wf, 'rank')
		json = nx.readwrite.json_graph.node_link_data(self.wf.graph)

		print(json)
		for node in sorted_tasks:
			self.assertTrue(rank_values[node] == int(self.wf.graph.nodes[node]['rank']))

	def test_schedule(self):
		retval = heft(self.wf)
		self.assertTrue(retval == 80)


class TestHeftMethodCalcTime(unittest.TestCase):
	def setUp(self):
		self.wf = Workflow(cfg.test_workflow_data['topcuoglu_graph'])
		env = Environment(cfg.test_workflow_data['topcuoglu_graph_system'])

		# self.wf = Workflow(cfg.test_heuristic_data['topcuoglu_graph'],
						# cfg.test_heuristic_data['topcuoglu_graph_system'])

		self.wf.add_environment(env)
	# self.wf.load_attributes(cfg.test_heuristic_data['flops_test_attr'])

	def test_schedule(self):
		retval = heft(self.wf)
		self.assertTrue(retval == 98)


# @unittest.skip('For now')
class TestPHeftMethods(unittest.TestCase):

	def setUp(self):
		self.wf = Workflow(cfg.test_heuristic_data['pheft_graph'])
		# self.wf.load_attributes(cfg.test_heuristic_data['pheft_attr'], calc_time=False)
		env = Environment(cfg.test_workflow_data['topcuoglu_graph_system'])
		self.wf.add_environment(env)
		self.up_oct_rank_values = [72, 41, 37, 43, 31, 41, 17, 20, 16, 0]
		self.up_rank_values = [169, 114, 102, 110, 129, 119, 52, 92, 42, 20]

	def tearDown(self):
		return -1

	def test_up_rank(self):
		upward_rank(self.wf)
		sorted_tasks = sort_tasks(self.wf, 'rank')
		for node in sorted_tasks:
			self.assertTrue(int(self.wf.graph.node[node]['rank']) ==
							self.up_rank_values[node])

	def test_oct_rank(self):
		oct_rank_matrix = dict()
		upward_oct_rank(self.wf, oct_rank_matrix)
		sorted_tasks = sort_tasks(self.wf, 'rank')
		for node in sorted_tasks:
			self.assertTrue(int(self.wf.graph.node[node]['rank']) ==
							self.up_oct_rank_values[node])

	def test_heft_schedule(self):
		# upward_rank(self.wf)
		retval = heft(self.wf)
		self.assertTrue(retval == 133)

	def test_pheft_schedule(self):
		# upward_rank(self.wf)
		retval = pheft(self.wf)
		self.assertTrue(retval == 122)


class TestDALiuGEGraph(unittest.TestCase):

	def setUp(self):
		self.wf = Workflow('test/data/daliugesample.json',
						cfg.test_heuristic_data['topcuoglu_graph_system'],
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
		# print(heft(self.wf))
		print(heft(self.dense))
		self.dense.pretty_print_allocation()

		# for p in self.dense.machines:
		# 	print(p)
		# #print(heft(self.gnp))

		pass
