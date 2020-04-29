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

from shadow.models.solution import Solution, Allocation
from shadow.models.globals import *

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

RAND_BOUNDS = 1000


def nsga2(wf, seed, generations=100, popsize=100):
	"""
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
	# Create a random parent population P size N
	n = popsize
	pop = generate_population(wf, seed, n)
	fronts = non_dom_sort(pop, objectives)
	Q = binary_tournament_rank(fronts)
	mutation()
	crossover()
	g = 0
	while g < generations:
		new_pop = []
		R = pop + Q
		non_dom_sort(R, objectives)
		crowding_distance(R)
		for soln in R:
			if len(new_pop) < popsize:
				new_pop.append(soln)

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
	population = []
	top_sort = generate_exec_orders(wf, popsize=size, seed=seed, skip_limit=skip_limit)
	for x in range(size):
		curr = next(top_sort)
		soln = generate_allocations(
			machines=wf.env.machines,
			task_order=curr,
			wf=wf,
			seed=seed
		)
		population.append(soln)

	return population


# How can we test non-domination? Need to get a testing set together for our HEFT graph

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
				p.dom_counter += 1  # This determines if it has been dominated
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


def binary_tournament_rank(pop):
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


def crowding_distance(solutions):
	"""
	For a given list of solutions, calculated the distance between the two closest solutions
	for a given dimension; that is, the next highest and next lowest solution for that dimension.
	:return:
	"""
	popsize = len(solutions)

	crowding_distance = []

	# Scores need to be normalised to the highest/lowest
	normalise_scores = None

	return None


def peek(iterable):
	try:
		first = next(iterable)
	except StopIteration:
		return None
	return first, itertools.chain([first], iterable)


def generate_exec_orders(wf, popsize, seed, skip_limit):
	top_sort_list = []
	generator = nx.all_topological_sorts(G=wf.graph)
	retval = peek(generator)
	if retval is None:
		return None

	random.seed(seed)
	while len(top_sort_list) < popsize:
		generator = nx.all_topological_sorts(G=wf.graph)
		for top in generator:
			# 'skip through' a number of different top sorts to ensure we are
			# getting a diverse range.
			skip = random.randint(0, RAND_BOUNDS) % skip_limit
			for x in range(skip):
				next(generator)
			yield top


# return top_sort_list


def calc_solution_cost(solution, workflow):
	cost = 0
	for machine in workflow.env.machines:
		for alloc in solution.list_machine_allocations(machine):
			runtime = alloc.aft - alloc.ast
			cost += workflow.env.calc_task_cost_on_machine(machine, runtime)
	return cost


def generate_allocations(machines, task_order, wf, seed):
	soln = NSGASolution(machines=machines)
	rand_bounds = len(machines)
	random.seed(seed)
	for t in task_order:
		index = random.randint(0, RAND_BOUNDS) % rand_bounds
		m = machines[index]
		calc_start_finish_times(t, m, wf, soln.list_machine_allocations(m))
		soln.add_allocation(t, m)
		if t.aft > soln.makespan:
			soln.makespan = t.aft

	soln.solution_cost = calc_solution_cost(soln, wf)

	return soln


def calc_start_finish_times(task, machine, workflow, curr_allocations):
	# For a given solution, we have task-machine pairs in a given order
	# This order will be based on the execution order provided by a topological sort
	st = 0
	predecessors = workflow.graph.predecessors(task)
	for pretask in predecessors:
		edge_comm_cost = 0
		if pretask.machine != machine:
			edge_comm_cost = workflow.graph.edges[pretask, task][WORKFLOW_DATASIZE]
		# If the finish time of the previous task is greater than st and communication cost, then we update the est
		if pretask.aft + edge_comm_cost >= st:
			st = pretask.aft + edge_comm_cost
	# Also need to check what the latest current allocation is on the machine

	num_alloc = len(curr_allocations)
	if num_alloc > 0:
		final = curr_allocations[num_alloc - 1]
		# This is in the event that the task execution order places tasks
		# with the same previous task on the same machine
		if final.aft > st:
			st = final.aft

	runtime = task.calc_runtime(machine)
	task.ast = st
	task.aft = task.ast + runtime
	task.machine = machine

	return None


class NSGASolution(Solution):
	""" A simple class to store each solutions' related information
	"""

	def __init__(self, machines):
		super().__init__(machines)
		self.dom_counter = 0
		self.nondom_rank = -1
		self.crowding_dist = -1
		self.solution_cost = 0
