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
import random

import networkx as nx

from test import config as cfg
from shadow.algorithms.metaheuristic import generate_population, \
	generate_allocations, \
	generate_exec_orders, \
	calc_start_finish_times, \
	non_dom_sort,\
	binary_tournament


from shadow.algorithms.fitness import calculate_fitness
from shadow.models.workflow import Workflow
from shadow.models.environment import Environment
from shadow.algorithms.heuristic import heft

current_dir = os.path.abspath('.')

logging.basicConfig(level="DEBUG")


class TestPopulationGeneration(unittest.TestCase):
	"""
	Tests how we generate solutions for NSGAII and SPEAII
	"""

	def setUp(self):
		self.wf = Workflow("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['topcuoglu_graph']))
		env = Environment("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['graph_sys_with_costs']))
		self.wf.add_environment(env)
		self.SEED = 10

	def test_generate_exec_orders(self):
		# Calling generate_exec_orders with a population of 1 should return a simple top sort
		top_sort = generate_exec_orders(self.wf, popsize=4, seed=self.SEED, skip_limit=1)
		# The result of running the above with self.SEED = 10, no skips is:
		# The first should always be 'order'
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
		# Generate allocations creates pairs. Solution is implied in allocation?
		top_sort = generate_exec_orders(self.wf, popsize=4, seed=self.SEED, skip_limit=1)
		curr = next(top_sort)
		machines = list(self.wf.env.machines)
		# Solution should contain allocations between tasks and machines
		soln = generate_allocations(machines, curr, self.wf, self.SEED)
		# Test seed is 10; RANDBOUNDS is 1000
		# first should be 0,0,1,2,0
		# For each Task in soln, we will have an allocation
		# e.g. tid=0, m='cat0_m0'.
		# If we go through each machine, and each task, the order should be
		##################  cat0_m1  |cat1_m1 | cat2_m2
		# task_alloc_order = [0, 1, 4, 5, 2, 6, 8, 3, 7, 9]
		# task_alloc_order = [0, 5, 4, 1, 2, 8, 3, 7, 9]
		alloc_sets = [
			{0, 5, 2, 6},
			{4, 1, 7},
			{3, 8, 9},
		]
		i = 0
		for machine in machines:
			x = len(alloc_sets[i] & set(soln.list_machine_allocations(machine)))
			self.assertEqual(x, 0)  # The difference between the sets should be 0

		self.assertEqual(soln.makespan, 107)
		# self.assertAlmostEqual(soln.solution_cost, 110.6, delta=0.01)


	def test_pop_gen(self):
		pop = generate_population(self.wf, size=4, seed=self.SEED, skip_limit=100)
		soln1 = pop[0]
		# First solution should be the same solution we have been working with previously.
		self.assertEqual(107, soln1.makespan)
		soln2 = pop[1]
		self.assertNotEqual(107, soln2.makespan)

	# self.assertEqual(soln.makespan,107)
	# This means we are dealing with a
	# what our the costs?

	@unittest.skip
	def test_nondomsort(self):
		pop = generate_population(self.wf, size=4, seed=self.SEED, skip_limit=100)
		seed = 10
		objectives = []
		# print(pop)
		non_dom_sort(pop, objectives)
		for p in pop:
			print(p.nondom_rank)


	# Playground test to print some values for the test data set
	# @unittest.skip
	def test_create_sample_pop(self):
		logging.debug("HEFT makespan".format(heft(self.wf).makespan))
		pop = generate_population(self.wf, size=4, seed=self.SEED, skip_limit=1)
		logging.debug("GA Initial Population")
		print("########################")
		for soln in pop:
			logging.debug(("Execution order: {0}".format(soln.execution_order)))
			logging.debug("Allocations: {0}".format(soln.list_all_allocations()))
			logging.debug("Makespan (s): {0}".format(soln.makespan))
			logging.debug("Cost ($){0}".format(calculate_fitness(['cost'],soln)))


class TestGASelectionMethods(unittest.TestCase):

	def setUp(self):
		self.wf = Workflow("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['topcuoglu_graph']))
		env = Environment("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['graph_sys_with_costs']))
		self.wf.add_environment(env)
		self.SEED = 10

	def test_binary_tournament(self):
		pop = generate_population(self.wf, size=4, seed=self.SEED, skip_limit=1)
		for soln in pop:
			soln.fitness = calculate_fitness(['time', 'cost'], soln)
		random.seed(self.SEED)
		parent1 = binary_tournament(pop)
		logging.debug(parent1.execution_order)
		parent2 = binary_tournament(pop)
		logging.debug(parent2.execution_order)
		self.assertSequenceEqual([0, 5, 3, 4, 2, 1, 6, 7, 8, 9],[t.tid for t in parent1.execution_order])
		logging.debug("Fitness: {0}".format(parent1.fitness))
		self.assertSequenceEqual([0, 5, 3, 4, 2, 1, 6, 8, 7, 9],[t.tid for t in parent2.execution_order])
		logging.debug("Fitness: {0}".format(parent2.fitness))


class TestNSGAIIMethods(unittest.TestCase):

	def setUp(self):
		self.wf = Workflow("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['topcuoglu_graph']))
		env = Environment("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['graph_sys_with_costs']))
		self.wf.add_environment(env)
		self.SEED = 10

	# These two are generated in the above tests, so we can garauntee their correctness
	def test_dominates(self):
		pop = generate_population(self.wf, size=4, seed=self.SEED, skip_limit=100)

	# This gives us 4 solutions with which to play

