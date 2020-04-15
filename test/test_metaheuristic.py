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


import unittest
import os
import logging

import networkx as nx

from test import config as cfg
from shadow.algorithms.metaheuristic import generate_population, \
	generate_allocations, \
	generate_exec_orders, \
	non_dom_sort

from shadow.classes.workflow import Workflow
from shadow.classes.environment import Environment

current_dir = os.path.abspath('.')


class TestPopulationGeneration(unittest.TestCase):
	"""
	Tests how we generate solutions for NSGAII and SPEAII
	"""

	def setUp(self):
		self.wf = Workflow("{0}/{1}".format(current_dir, cfg.test_workflow_data['topcuoglu_graph']))
		env = Environment("{0}/{1}".format(current_dir, cfg.test_workflow_data['topcuoglu_graph_system']))
		self.wf.add_environment(env)
		self.SEED = 10

	def test_generate_exec_orders(self):
		# Calling generate_exec_orders with a population of 1 should return a simple top sort
		top_sort = generate_exec_orders(self.wf, popsize=4, seed=self.SEED, skip_limit=1)
		# The result of running the above with self.SEED = 10, no skips is:
		# The first should always be
		# bitwise set &
		order = [0, 5, 4, 3, 2, 6, 1, 8, 7, 9]
		curr = next(top_sort)
		# Check that a comparison between top_sort and the correct order is correct
		sum = 0
		for i in range(len(order)):
			if curr[i].tid != order[i]:
				sum += 1
		self.assertEqual(sum, 0)

		curr = next(top_sort)
		for i in range(len(order)):
			if curr[i].tid != order[i]:
				sum += 1
		self.assertGreater(sum, 0)

	def test_generate_allocations(self):
		seed = 10
		# We have a workflow, and an environment on which the workflow is being executed
		tasks = self.wf.tasks
		machines = self.wf.env.machines

		solution = generate_allocations()

	# print(a)
	# a = generate_allocations(self.wf.graph.number_of_nodes(),10, 4,seed)
	# print(a)

	def test_pop_gen(self):
		seed = 10
		a = generate_population(self.wf, 10, seed, 2)
		# for x in a:
		#     print(x.task_order)
		b = generate_population(self.wf, 10, seed, 2)

		self.assertTrue(a == a)
		seed = 47

		b = generate_population(self.wf, 10, seed, 2)
		self.assertFalse(a == b)

	# for soln in a:
	#     print(soln.task_assign)

	def test_nondomsort(self):
		seed = 10
		pop = generate_population(self.wf, 10, seed, 2)
		objectives = []
		# print(pop)
		non_dom_sort(pop, objectives)
		for p in pop:
			print(p.nondom_rank)
