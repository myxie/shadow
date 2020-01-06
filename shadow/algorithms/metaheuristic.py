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

# This file contains code for implementing metaheuristic scheduling algorithms.
# Currently, this file implements the following algorithms:
# 

import networkx as nx
import itertools
import random

# TODO; initial setup required for a genetic algorithm
# TODO; initial setup required for an evolutionary algorithm 6

"""
From Yu, Kirley & Buyya 2007
NSGAII* and SPEAII*: 
1. Generate intial population
do:
    2. crossover on individuals
    3. perform mutation on offspring
    4. evaluate current solutions
    5. select individuals to be carried onto next generation
while(termination condition not satisfied)

The two differ on evaluation and selection strategy
"""


def nsga2(wf, seed, generations=100, popsize=100):
	"""
	Create a random parent population P size N
	Apply non-dominated sort to P
	Binary tournament selection to create population Q, size N
	For each generation, taking the most recent sets P and Q:
		Combine the populations to make R, size 2N
		Apply non-dominated sort to R
		Starting from the first Front:
			If we can add all solutions from the current front to the new
			population, Pt+1, without going over the population limit N, add the
			front to Pt+1
			When an overlap on a Front Fl occurs, in which adding all solutions
			from the front would cause size(Pt+1) > N, we sort all solutions
			from this last front, FL, using the crowded comparison operator, in
			descending order, and choose the best solutions to fill remaining
			slots.

			We then use tournament selection again to create Q, and start again
			generation_counter++

	Whilst we have not reached our terminal condition, do:
		crossover on individual solutions
		mutate the offspring
		evaluate the quality of the solutions
		select individuals to carry over to the new population
	"""

	objectives = []
	pop = generate_population(wf, seed)
	non_dom_sort(pop, objectives)

	return None


def spea2(wf, seed):
	generate_population(wf, seed)
	return None


def generate_population(wf, size, seed, skip_limit):
	"""
	task_assign[0] is the resource to which Task0 is assigned
	task_order[0] is the task that will be executed first

	each 'solution' should be a tuple of a task-assign and exec-order solution

	In the future it might be useful, in addition to checking feasibility of solution, to minimise duplicates of the population generated. Not sure about this.
	"""
	pop = [Solution() for x in range(size)]

	# In order to generate solutions, we need to ensure that
	exec_order = generate_exec_orders(wf, size, seed, skip_limit)

	# Generate a list of task/resource assignments
	task_assign = generate_allocations(wf.graph.number_of_nodes(), size, 4, seed)

	if len(pop) != len(exec_order) or len(pop) != len(task_assign):
		return None
	else:
		for soln in pop:
			soln.exec_order = exec_order.pop()
			soln.task_assign = task_assign.pop()

	return pop


def non_dom_sort(pop, objectives):
	front = {0: []}
	dominated = {}
	for p in pop:
		p.dom_counter = 0  # reset between different sorts, as may have changed
		for q in pop:
			if dominates(p, q, objectives):  # if p dominates q
				if p not in dominated:
					dominated[p] = [q]
				else:
					dominated[p] += [q]  # add q to set of soln dominated by p
			elif dominates(q, p, objectives):
				p.dom_counter += 1
		if p.dom_counter == 0:
			p.nondom_rank = 1
			front[0].append(p)

	i = 1

	if i in front:
		Q = []
		for p in front[i]:
			for q in dominated[p]:
				q.dom_counter -= 1
				if q.dom_counter == 0:
					q.nondom_rank = i + 1
					Q.append(q)
		i += 1
		front[i] = Q

	return None


def dominates(p, q, objective_set):
	"""
	Checks if the given solution 'p' dominates 'q' for each objective outlined
	in 'objective set'
	"""

	return True


def binary_tournament(pop):
	return None


def crossover(soln):
	"""
	As described in Yu & Buyya 2007

	Two step approach:
	1. Two parents are selected at random from population
	2. Two random points are selected from the task-assignment strings
	3. all tasks between the points are chosen as crossover points
	4. the service allocation of the tasks within the crossover points are exchanged.
	"""
	return None


def mutation(soln):
	"""
	Mutation requires us to separate the nodes into levels of nodes that are
	independent of each other with respect to precedence:

	Level 0 should have just the first task(s) - those with no indegree
	Level n should have just the final task(s) - those with no outdegree
	"""

	return None


def crowding_distance():
	return None


def peek(iterable):
	try:
		first = next(iterable)
	except StopIteration:
		return None
	return first, itertools.chain([first], iterable)


def generate_exec_orders(wf, popsize, seed, skip_limit):
	top_sort_list = []
	generator = nx.all_topological_sorts(wf.graph)
	retval = peek(generator)
	if retval is None:
		return None
	else:
		first, generator = retval
		top_sort_list.append(first)

	# Generate a list of topological sorts
	random.seed(seed)
	while len(top_sort_list) < popsize:
		generator = nx.all_topological_sorts(wf.graph)
		for top in generator:
			# 'skip through' a number of different top sorts to ensure we are
			# getting a diverse range.
			skip = random.randint(0, 100) % skip_limit
			for x in range(skip):
				next(generator)
			top_sort_list.append(list(top))
			if len(top_sort_list) == popsize:
				break

	return top_sort_list


def generate_allocations(num_nodes, popsize, num_resource, seed):
	alloc_list = []
	random.seed(seed)
	for x in range(popsize):
		alloc_list.append(
			[random.randint(0, 1000) % num_resource for x in range(num_nodes)])
	return alloc_list


class Solution:
	""" A simple class to store each solutions' related information
	"""
	task_assign = []
	exec_order = []
	dom_counter = 0
	nondom_rank = -1
	crowding_dist = -1

	def _is_feasible(task_order):
		"""
		Check that task_order is a valid topological sort
		"""
		return True
