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

import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import networkx as nx

from test import config as cfg
from shadow.algorithms.metaheuristic import generate_population, \
	generate_allocations, \
	generate_exec_orders, \
	calc_start_finish_times, \
	non_dom_sort, \
	binary_tournament, \
	crossover,\
	mutation



from shadow.algorithms.fitness import calculate_fitness
from shadow.models.workflow import Workflow, Task
from shadow.models.environment import Environment
from shadow.algorithms.heuristic import heft
from shadow.algorithms.metaheuristic import GASolution

current_dir = os.path.abspath('.')

logging.basicConfig(level="DEBUG")
logger = logging.getLogger(__name__)


class TestPopulationGeneration(unittest.TestCase):
	"""
	Tests how we generate solutions for NSGAII and SPEAII
	"""

	def setUp(self):
		self.wf = Workflow("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['topcuoglu_graph']))
		env = Environment("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['graph_sys_with_costs']))
		self.wf.add_environment(env)
		self.rng = np.random.default_rng(40)

	def test_generate_exec_orders(self):
		"""
		Expected results from creating a topological sort of `self.wf` for a
		given population size. The `skip_limit` in this example is 1,
		which means that if we were to generate a population of execution
		orders, we would go through all topological sorts without skipping any.

		Population size: 4
		Skip limit - 1
		rng = default_rng(40) (This is specified in setUp).

		With `skip_limit=1`, the first top_sort created will be:

			[0, 5, 4, 3, 2, 6, 1, 8, 7, 9]

		Test 1: Check to make sure the expected topological sort generated is
		the one we get from `generate_exec_orders`

		Test 2: Check that the next topological sort is different - that is,
		we are not generating the same TopSort over and over again.

		Returns
		-------
		Pass/Fail
		"""

		# Test 1
		top_sort = generate_exec_orders(self.wf, popsize=4, rng=self.rng, skip_limit=1)
		order = [0, 5, 4, 3, 2, 6, 1, 8, 7, 9]
		curr = next(top_sort)
		sum = 0
		for i in range(len(order)):
			if curr[i].tid != order[i]:
				sum += 1
		self.assertEqual(sum, 0)

		# Test 2
		curr = next(top_sort)
		for i in range(len(order)):
			if curr[i].tid != order[i]:
				sum += 1
		self.assertGreater(sum, 0)

	def test_calc_start_finish_time(self):
		"""
		Given a 'randomly' generated Solution, ensure that we calculate the
		correct start and finish times for the random allocation.

		Test 1: Duplicates `test_generate_exec_orders` to confirm RNG returns
		the same values for the same function parameters.

		Test 2: Initial conditions, where there are no allocations already in
		the solution


		Returns
		-------
		Pass/Fail
		"""

		# Test 1
		top_sort = generate_exec_orders(
			self.wf, popsize=4, rng=self.rng, skip_limit=1
		)
		curr = next(top_sort)
		self.assertListEqual(
			[x.tid for x in curr],
			[0, 5, 4, 3, 2, 6, 1, 8, 7, 9]
		)
		machine = 0

		solution = GASolution
		ast, aft = calc_start_finish_times(
			curr[0], 0, self.wf, solution
		)

	def test_generate_allocations(self):
		"""
		After generating an execution order, we need to allocate tasks to
		machines whilst maintaining precedence constraints.

		Test 1: Duplicates `test_generate_exec_orders`


		Test2: Generate a list of allocations, and creates a set from this
		list of IDs. This compare to a list of sets; the difference between
		each set (which represents task-machin pairings) should be 0.


		Returns
		-------

		"""
		top_sort = generate_exec_orders(
			self.wf, popsize=4, rng=self.rng, skip_limit=1
		)
		curr = next(top_sort)
		self.assertListEqual(
			[x.tid for x in curr],
			[0, 5, 4, 3, 2, 6, 1, 8, 7, 9]
		)
		machines = list(self.wf.env.machines)
		# Solution should contain allocations between tasks and machines
		soln = generate_allocations(machines, curr, self.wf, self.rng)

		# first should be 0,0,1,2,0
		# For each Task in soln, we will have an allocation
		# e.g. tid=0, m='cat0_m0'.
		# If we go through each machine, and each task, the order should be
		##################  cat0_m1  |cat1_m1 | cat2_m2
		# task_alloc_order = [0, 1, 4, 5, 2, 6, 8, 3, 7, 9]
		# task_alloc_order = [0, 5, 4, 1, 2, 8, 3, 7, 9]
		alloc_sets = [
			{0, 5, 4, 8,7},
			{6,9},
			{3, 2, 1},
		]
		i = 0
		for machine in machines:
			x = len(alloc_sets[i] & set(soln.list_machine_allocations(machine)))
			self.assertEqual(x, 0)

		self.assertEqual(soln.makespan, 107)

	# self.assertAlmostEqual(soln.solution_cost, 110.6, delta=0.01)

	def test_pop_gen(self):
		pop = generate_population(
			self.wf, size=25, rng=self.rng, skip_limit=5
		)
		soln1 = pop[0]
		# First solution should be the same solution we
		# have been working with previously.
		self.assertEqual(107, soln1.makespan)
		soln2 = pop[2]
		self.assertNotEqual(114, soln2.makespan)
		soln5 = pop[4]
		self.assertEqual(145, soln5.makespan)
		soln25 = pop[24]
		self.assertEqual(130, soln25.makespan)

	# self.assertEqual(soln.makespan,107)
	# This means we are dealing with a
	# what our the costs?

	@unittest.skip
	def test_nondomsort(self):
		pop = generate_population(self.wf, size=4, rng=self.rng, skip_limit=100)
		seed = 10
		objectives = []
		# print(pop)
		non_dom_sort(pop, objectives)
		for p in pop:
			print(p.nondom_rank)


	def test_create_sample_pop(self):
		logger.debug("HEFT makespan {0}".format(heft(self.wf).makespan))
		pop = generate_population(self.wf, size=25, rng=self.rng, skip_limit=5)
		for soln in pop:
			self.assertEqual(soln.execution_order[-1].task.aft,soln.makespan)
		logger.debug("GA Initial Population")
		logger.debug("########################")
		for soln in pop:
			logger.debug(("Execution order: {0}".format(soln.execution_order)))
			logger.debug("Allocations: {0}".format(soln.list_all_allocations()))
			logger.debug("Makespan (s): {0}".format(calculate_fitness(['time'], soln)))
			logger.debug("Cost ($){0}".format(calculate_fitness(['cost'], soln)))

			soln.fitness = calculate_fitness(['time', 'cost'], soln)
		fig, ax = plt.subplots()
		ax.set_xlim([90,200])
		ax.set_ylim([100,250])
		x = [soln.fitness['time'] for soln in pop]
		y = [soln.fitness['cost'] for soln in pop]
		ax.scatter(x, y, c='red')
		ax.set_axisbelow(True)
		ax.legend()
		ax.grid(True)
		plt.xlabel('Solution Runtime')
		plt.ylabel('Solution execution cost')
		plt.show()


class TestGASelectionMethods(unittest.TestCase):

	def setUp(self):
		self.wf = Workflow(
			"{0}/{1}".format(
				current_dir, cfg.test_metaheuristic_data['topcuoglu_graph']
			)
		)
		env = Environment(
			"{0}/{1}".format(
				current_dir, cfg.test_metaheuristic_data['graph_sys_with_costs']
			)
		)
		self.wf.add_environment(env)
		self.rng = np.random.default_rng(40)

	def test_binary_tournament(self):
		pop = generate_population(self.wf, size=25, rng=self.rng, skip_limit=5)
		for soln in pop:
			soln.fitness = calculate_fitness(['time', 'cost'], soln)
		compare_prob = 0.5
		parent1 = binary_tournament(pop,compare_prob,self.rng)
		logger.debug(parent1.execution_order)
		compare_prob = 0.7
		parent2 = binary_tournament(pop,compare_prob,self.rng)
		# parent2 = binary_tournament(pop, self.rng)
		logger.debug(parent2.execution_order)
		self.assertSequenceEqual(
			[0, 5, 3, 4, 2, 1, 6, 8, 7, 9],
			[t.task.tid for t in parent1.execution_order]
		)
		logger.debug("Fitness: {0}".format(parent1.fitness))
		self.assertSequenceEqual(
			[0, 5, 4, 1, 3, 2, 8, 6, 7, 9],
			[t.task.tid for t in parent2.execution_order]
		)
		logger.debug("Fitness: {0}".format(parent2.fitness))
		#
		#
		# fig, ax = plt.subplots()
		# x = [soln.fitness['time'] for soln in pop]
		# y = [soln.fitness['cost'] for soln in pop]
		# ax.set_xlim([90,200])
		# ax.set_ylim([100,170])
		# ax.grid(True)
		# ax.scatter(x, y, c='red')
		# ax.set_axisbelow(True)
		# selectedx = [parent1.fitness['time'], parent2.fitness['time']]
		# selectedy = [parent1.fitness['cost'], parent2.fitness['cost']]
		# ax.scatter(selectedx, selectedy, c='blue')
		# ax.legend()
		# plt.xlabel('Solution Runtime')
		# plt.ylabel('Solution execution cost binary')

		# plt.show()

	def test_crossover(self):
		pop = generate_population(self.wf, size=25, rng=self.rng,
								  skip_limit=5)
		for soln in pop:
			soln.fitness = calculate_fitness(['time', 'cost'], soln)

		random.seed(self.rng)

		p1 = binary_tournament(pop)
		self.assertSequenceEqual(
			[0, 5, 3, 2, 1, 4, 7, 8, 6, 9],
			[t.task.tid for t in p1.execution_order]
		)
		p2 = binary_tournament(pop)
		self.assertSequenceEqual(
	[0, 5, 4, 1, 3, 2, 8, 6, 7, 9],
			[t.task.tid for t in p2.execution_order]
		)
		c1, c2 = crossover(p1, p2, self.wf)
		p1order = [t.task.tid for t in p1.execution_order]
		c1order = [t.task.tid for t in c1.execution_order]
		self.assertSequenceEqual(p1order, c1order)
		for m in c1.machines:
			for allocation in c1.list_machine_allocations(m):
				if allocation.task.tid == 4:
					self.assertEqual('cat1_m1', allocation.machine.id)
		for m in c2.machines:
			for allocation in c2.list_machine_allocations(m):
				if allocation.task.tid == 4:
					self.assertEqual('cat0_m0', allocation.machine.id)
		self.assertNotEqual(p2.makespan, c2.makespan)

		fig, ax = plt.subplots()
		c1.fitness = calculate_fitness(['time', 'cost'], c1)
		c2.fitness = calculate_fitness(['time', 'cost'], c2)
		crossx = [c1.fitness['time'], c2.fitness['time']]
		crossy = [c1.fitness['cost'], c2.fitness['cost']]
		ax.scatter(crossx, crossy, c='green')
		x = [soln.fitness['time'] for soln in pop]
		y = [soln.fitness['cost'] for soln in pop]
		ax.grid(True)
		ax.set_xlim([90,200])
		ax.set_ylim([100,170])
		ax.scatter(x, y, c='red')
		ax.set_axisbelow(True)
		selectedx = [p1.fitness['time'], p2.fitness['time']]
		selectedy = [p1.fitness['cost'], p2.fitness['cost']]
		ax.scatter(selectedx, selectedy, c='blue')
		ax.legend()
		plt.xlabel('Solution Runtime')
		plt.ylabel('Solution execution cost')
		plt.show()


	def test_mutation(self):
		pop = generate_population(self.wf, size=25, rng=self.rng,
								  skip_limit=5)
		for soln in pop:
			soln.fitness = calculate_fitness(['time', 'cost'], soln)

		random.seed(self.rng)

		p1 = binary_tournament(pop,self.rng, 0.6)
		self.assertSequenceEqual([0, 5, 3, 2, 1, 4, 7, 8, 6, 9],
								 [t.task.tid for t in p1.execution_order])

		mutated_child = mutation(p1, self.wf,'swapping',rng=self.rng)
		mutated_order_swapped = [0,5,3,1,7,4,2,8,6,9]
		self.assertSequenceEqual(mutated_order_swapped, [alloc.task.tid for alloc in mutated_child.execution_order])
		selected_machine = None
		for machine in mutated_child.machines:
			if machine.id == 'cat2_m2':
				selected_machine = machine
		mutated_alloc = mutated_child.list_machine_allocations(selected_machine)
		self.assertSequenceEqual([7,2,9],[alloc.task.tid for alloc in mutated_alloc])


	def test_overall(self):
		total_generations = 25
		crossover_probability = 0.5
		mutation_probability = 0.4
		popsize = 25
		pop = generate_population(
			self.wf,
			size=popsize,
			rng=self.rng,
			skip_limit=5
		)
		for soln in pop:
			soln.fitness = calculate_fitness(['time','cost'],soln)

		generations = []
		x = [soln.fitness['time'] for soln in pop]
		y = [soln.fitness['cost'] for soln in pop]
		weights = [200 * i for i in Counter(x).values() for j in range(i)]

		generations.append((x,y))
		parents1 = []
		parents2 = []
		for gen in range(total_generations):
			new_pop = []
			parent1= None
			parent2 = None
			while len(new_pop) < len(pop):
				p1 = binary_tournament(pop,0.5,self.rng)
				p2 = binary_tournament(pop,0.5,self.rng)
				parent1 = p1
				parent2 = p2
				if random.random() < crossover_probability:
					c1, c2 = crossover(p1,p2,self.wf)
					new_pop.append(c1)
					new_pop.append(c2)
				elif random.random() < mutation_probability:
					c1 = mutation(p1, self.wf, 'swapping',rng=self.rng)
					if c1 is None:
						# The mutation didn't occur due to selection issue
						continue
					new_pop.append(c1)
				else:
					new_pop.append(p1)
					new_pop.append(p2)
					continue
			tmp_pop = pop + new_pop
			for soln in tmp_pop:
				soln.fitness = calculate_fitness(['time', 'cost'],soln)
				# soln.total_fitness = soln.calc_total_fitness()
			tmp_pop.sort(key=lambda x: (x.fitness['time'], x.fitness['cost']))
			# tmp_pop.sort(key=lambda solution: solution.total_fitness)
			pop = tmp_pop[0:popsize]
			weights = [10*i for i in Counter(x).values() for j in range(i)]
			x = [soln.fitness['time'] for soln in pop]
			y = [soln.fitness['cost'] for soln in pop]
			parent1_x = [parent1.fitness['time']]
			parent1_y = [parent1.fitness['cost']]
			parent2_x = [parent2.fitness['time']]
			parent2_y = [parent2.fitness['cost']]
			generations.append((x,y))
			parents1.append((parent1_x,parent1_y))
			parents2.append((parent2_x, parent2_y))
			plt.draw()
			plt.show()

		for soln in pop:
			logger.info(soln.fitness)

		fig, ax = plt.subplots()
		ax.set_xlim([80, 250])
		ax.set_ylim([100, 250])
		scatter = ax.scatter(generations[0][0], generations[0][1],c='blue',alpha=.2, label='New Pop')
		parent_scatter = ax.scatter(parents1[0][0], parents1[0][1], c='red', alpha=0.8, label='Parent 1')
		parent2_scatter = ax.scatter(parents2[0][0], parents1[0][1], c='red', alpha=0.8, label = 'Parent 2')
		ax.legend()

		def animate(i):
			scatter.set_offsets(np.c_[generations[i][0],generations[i][1]])
			parent_scatter.set_offsets(np.c_[parents1[i][0], parents1[i][1]])
			parent2_scatter.set_offsets(np.c_[parents2[i][0], parents2[i][1]])
			ax.set_xlabel('Runtime (s) \n Generation {0}'.format(i))
			ax.set_ylabel('Cost ($)')

		anim = FuncAnimation(
			fig, animate, interval=100, frames=25)

		plt.draw()

		anim.save('filename.mp4', fps=1)

class TestNSGAIIMethods(unittest.TestCase):

	def setUp(self):
		self.wf = Workflow("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['topcuoglu_graph']))
		env = Environment("{0}/{1}".format(current_dir, cfg.test_metaheuristic_data['graph_sys_with_costs']))
		self.wf.add_environment(env)
		self.rng = 10

		# These two are generated in the above tests, so we can garauntee their correctness
	def test_dominates(self):
		pop = generate_population(self.wf, size=4, rng=self.rng, skip_limit=100)

# This gives us 4 solutions with which to play
