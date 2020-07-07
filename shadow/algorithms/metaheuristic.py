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

# """
# N = population size
# P = create parent population by randomly creating N individuals
# while not done
#     C = create empty child population
#     while not enough individuals in C
#         parent1 = select parent   ***** HERE IS WHERE YOU DO TOURNAMENT SELECTION *****
#         parent2 = select parent   ***** HERE IS WHERE YOU DO TOURNAMENT SELECTION *****
#         child1, child2 = crossover(parent1, parent2)
#         mutate child1, child2
#         evaluate child1, child2 for fitness
#         insert child1, child2 into C
#     end while
#     P = combine P and C somehow to get N new individuals
# end while
# """

import networkx as nx
import itertools
import random
import copy

from shadow.models.solution import Solution, Allocation
from shadow.models.globals import *
from shadow.algorithms import fitness

import logging

logger = logging.getLogger(__name__)

# TODO; initial setup required for a genetic algorithm
# TODO; initial setup required for an evolutionary algorithm 6
#
# """
# From Yu, Kirley & Buyya 2007
# NSGAII* and SPEAII*:
# 1. Generate intial population
# do:
#     2. crossover on individuals
#     3. perform mutation on offspring
#     4. evaluate current solutions
#     5. select individuals to be carried onto next generation
# while(termination condition not satisfied)
#
# The two differ on evaluation and selection strategy
# """

RAND_BOUNDS = 1000
DEFAULT_SEED = 50


class GASolution(Solution):
	def __init__(self, machines):
		super().__init__(machines)
		# Fitness is a dictionary of objectives and the calculated fitness
		self.fitness = {}
		self.total_fitness = None

	def calc_total_fitness(self):
		total = 0
		for objective in self.fitness:
			total += self.fitness[objective]
		return total


def ga(workflow,
	   objectives,
	   seed,
	   mutation_probability,
	   crossover_probability,
	   generations=100,
	   popsize=100):
	"""
	This function runs a standard genetic algorithm, with basic elitism, and
	basic diversification. The algorithm:

		* Generates a population of Solutions, based on the workflow provided
		* For a given number of generations:

			* Create a child population (newgen)
			* While the newgen < pop
				* Select parents using binary tournament seleciton
				* Crossover the parents to children
				* mutate the children
				* calculate the fitness of each child
				* add new  children to newgen

			* Keep as many children as there are that outperform the parents

	:param mutation_probability:
	:param crossover_probability:
	:param workflow:
	:param objectives:
	:param seed:
	:param generations:
	:param popsize:
	:return:
	"""

	pop = generate_population(workflow, seed, generations, popsize)
	for soln in pop:
		soln.fitness = fitness.calculate_fitness(objectives, soln)
	# binary_tournament(pop)
	generation = 0
	limit = False
	while generation < generations or limit:
		newgen = []
		while len(newgen) > len(pop):
			p1 = binary_tournament(pop)
			p2 = binary_tournament(pop)
			c1, c2 = crossover(p1, p2, seed)
			for c in [c1, c2]:
				mutation(c)
				fitness.calculate_fitness(c, objectives)
				newgen.append(c)
		generation += 1
		continue
	pass


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


#
#
# def spea2(wf, seed):
# 	generate_population(wf, seed)
# 	return None


################################################################################
################################################################################
#    							HELPER FUNCTIONS							   #
################################################################################
################################################################################

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
# OR WE CAN USE A DIFFERENT GRAPH :O

def binary_tournament(pop, seed=DEFAULT_SEED):
	"""
	Stock standard binary tournament selection
	:param pop: population of solutions
	:param seed: Random seed value for repeatability
	:return: selected parent for crossover
	"""
	# random.seed(seed)

	k = 2  # BINARY tournament selection
	best = None
	# Get two random solutions from the population
	t1, t2 = random.sample(pop, k)
	return compare_fitness(t1, t2, [0.5, 0.5])


def compare_fitness(soln1, soln2, weights, comparison=min):
	if len(soln1.fitness) != len(soln2.fitness) or len(weights) != len(soln1.fitness):
		raise ValueError("Solutions have diferent numbers of fitness scores")

	s1fit = sum(soln1.fitness.values()) * weights[0]
	s2fit = sum(soln1.fitness.values()) * weights[1]

	if comparison(s1fit, s2fit) == s1fit:
		return soln1
	else:
		return soln2


def crossover(parent1, parent2, seed=DEFAULT_SEED):
	"""
	As described in Yu & Buyya 2007

	Two step approach:
	1. Two parents are selected at random from population
	2. Two random points are selected from the task-assignment strings
	3. all tasks between the points are chosen as crossover points
	4. the service allocation of the tasks within the crossover points are exchanged.
	"""

	p1, p2 = create_window(parent1, parent2, seed)
	# We achieve the crossover by finding the 'like tasks' between the boundary and swapping
	# Them between parents.
	pairs = parent1.task_machine_pairs()
	c1, c2 = copy.deepcopy(p1), copy.deepcopy(p2)
	tasks = parent1.execution_order[p1:p2]
	for task in tasks:
		m = task.machine
	return c1, c2


def create_window(parent1, parent2, seed=DEFAULT_SEED):
	random.seed(seed)
	# Select two random points as our 'window'
	p1 = random.randint(1, len(parent1.execution_order) - 1)
	p2 = random.randint(1, len(parent2.execution_order))
	if p2 <= p1:
		tmp = p1
		p1 = p2
		p2 = tmp
	return p1, p2


def mutation(soln):
	"""
	Mutation requires us to separate the nodes into levels of nodes that are
	independent of each other with respect to precedence:

	Level 0 should have just the first task(s) - those with no indegree
	Level n should have just the final task(s) - those with no outdegree
	"""

	return None


def peek(iterable):
	try:
		first = next(iterable)
	except StopIteration:
		return None
	return first, itertools.chain([first], iterable)


def generate_exec_orders(wf, popsize, seed, skip_limit):
	top_sort_list = []
	gen = nx.all_topological_sorts(G=wf.graph)
	retval = peek(gen)
	if retval is None:
		return None

	random.seed(seed)
	while len(top_sort_list) < popsize:
		gen = nx.all_topological_sorts(G=wf.graph)
		for top in gen:
			# 'skip through' a number of different top sorts to ensure we are
			# getting a diverse range.
			skip = random.randint(0, RAND_BOUNDS) % skip_limit
			for x in range(skip):
				next(gen)
			yield top


# return top_sort_list

def calc_solution_cost(solution, workflow):
	cost = 0
	for machine in workflow.env.machines:
		for alloc in solution.list_machine_allocations(machine):
			runtime = alloc.aft - alloc.ast
			cost += workflow.env.calc_task_cost_on_machine(machine, runtime)
	return cost


def generate_allocations(machines, task_order, wf, seed, solution_class=GASolution):
	soln = solution_class(machines=machines)
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


def solution_calculation_updates():
	### This function is for when we crossover or mutate and need to recalculate
	### Machine assignments have been done, we just want to go through the order
	### and double check allocations.
	return None


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
		if not _check_machine_availability(workflow.solution, machine, st, task):
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


def _check_machine_availability(solution, machine, start_time, task):
	for alloc in solution.list_machine_allocations(machine):
		if alloc.ast <= start_time < alloc.aft:
			return False
		# if it starts beforehand but will over-run:
		if start_time < alloc.ast <= start_time + task.calculated_runtime[machine]:
			return False


###### NSGAII Specific functions #####

def binary_tournament_rank(pop):
	return None


def non_dom_sort(pop, objectives, env):
	front = {0: []}
	dominated = {}
	for p in pop:
		p.dom_counter = 0  # reset between different sorts, as may have changed
		for q in pop:
			if p is q:
				continue
			if dominates(p, q, objectives, env):  # if p dominates q
				if p not in dominated:
					dominated[p] = [q]
				else:
					dominated[p] += [q]  # add q to set of soln dominated by p
			elif dominates(q, p, objectives, env):
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

	return front


def dominates(p, q, objective_set, env):
	"""
	Checks if the given solution 'p' dominates 'q' for each objective outlined
	in 'objective set'
	"""

	p_sol = []
	# objective is a function
	for objective in objective_set:
		p_sol.append(objective(p, env))

	return True


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


class NSGASolution(Solution):
	""" A simple class to store each solutions' related information
	"""

	def __init__(self, machines):
		super().__init__(machines)
		self.dom_counter = 0
		self.nondom_rank = -1
		self.crowding_dist = -1
		self.solution_cost = 0
