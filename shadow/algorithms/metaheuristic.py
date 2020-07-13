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
from shadow.models.workflow import Task
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
			task_order=(curr),
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
	return compare_fitness(t1, t2, [0.8, 0.2], 0.8)


def compare_fitness(soln1, soln2, weights, probfit, comparison=min):
	if len(soln1.fitness) != len(soln2.fitness) or len(weights) != len(soln1.fitness):
		raise ValueError("Solutions have diferent numbers of fitness scores")

	fitlist = [soln1, soln2]
	rev = False
	if comparison is max:
		rev = True

	fitlist.sort(key=lambda x: (x.fitness['time']*weights[0], x.fitness['cost']*(weights[1])), reverse=rev)
	if random.random() < probfit:
		return fitlist[0]
	else:
		return random.sample(fitlist,1)[0]


def crossover(parent1, parent2, workflow, seed=DEFAULT_SEED):
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
	# machines = copy.deepcopy(parent1.machines)
	c1, c2 = GASolution(parent1.machines), GASolution(parent2.machines)
	# c1.execution_order = copy.deepcopy(parent1.execution_order)
	# c2.execution_order = copy.deepcopy(parent2.execution_order)

	crossover_tasks = [allocation.task.tid for allocation in parent1.execution_order[p1:p2]]
	c1_crossover_m, c2_crossover_m = [], []
	# These are the machine allocations for each task/pair swap
	c1_tmp_alloc = []
	c2_tmp_alloc = []
	for m in parent1.machines:
		for alloc in parent1.list_machine_allocations(m):
			if alloc.task.tid in crossover_tasks:
				continue
			else:
				nalloc = copy.deepcopy(alloc)
				nalloc.reset()
				c1_tmp_alloc.append(nalloc)
		for alloc in parent2.list_machine_allocations(m):
			if alloc.task.tid in crossover_tasks:
				continue
			else:
				nalloc = copy.deepcopy(alloc)
				nalloc.reset()
				c2_tmp_alloc.append(nalloc)

	for m in parent1.machines:
		for alloc in parent2.list_machine_allocations(m):
			if alloc.task.tid in crossover_tasks:
				nalloc = copy.deepcopy(alloc)
				nalloc.reset()
				c1_tmp_alloc.append(nalloc)
		for alloc in parent1.list_machine_allocations(m):
			if alloc.task.tid in crossover_tasks:
				nalloc = copy.deepcopy(alloc)
				nalloc.reset()
				c2_tmp_alloc.append(nalloc)

	c1taskorder = [alloc.task.tid for alloc in parent1.execution_order]
	c1_tmp_alloc.sort(key=lambda x: c1taskorder.index(x.task.tid))
	c2taskorder = [alloc.task.tid for alloc in parent2.execution_order]
	c2_tmp_alloc.sort(key=lambda x: c2taskorder.index(x.task.tid))

	for alloc in c1_tmp_alloc:
		t = alloc.task
		m = alloc.machine
		calc_start_finish_times(
			task=t,
			machine=m,
			workflow=workflow,
			curr_allocations=c1.list_machine_allocations(m),
			solution=c1
		)
		alloc = Allocation(alloc.task, alloc.machine)
		c1.allocations[m.id].append(alloc)
		c1.execution_order.append(alloc)
		c1.task_allocations[t] = alloc
		if t.aft > c1.makespan:
			c1.makespan = t.aft

	for alloc in c2_tmp_alloc:
		t = alloc.task
		m = alloc.machine
		calc_start_finish_times(
			task=t,
			machine=m,
			workflow=workflow,
			curr_allocations=c2.list_machine_allocations(m),
			solution=c2
		)
		alloc = Allocation(alloc.task, alloc.machine)
		c2.allocations[m.id].append(alloc)
		c2.execution_order.append(alloc)
		c2.task_allocations[t] = alloc
		if t.aft > c2.makespan:
			c2.makespan = t.aft
	# 	index = random.randint(0, RAND_BOUNDS) % rand_bounds
	# 	m = machines[index]
	# 	calc_start_finish_times(t, m, wf, soln.list_machine_allocations(m))
	# 	soln.add_allocation(t, m)
	# 	if t.aft > soln.makespan:
	# 		soln.makespan = t.aft
	#
	# soln.solution_cost = calc_solution_cost(soln, wf)

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


def mutation(solution, workflow, mutation_type='swapping', seed=None):
	"""
	Mutation requires us to separate the nodes into levels of nodes that are
	independent of each other with respect to precedence:

	Level 0 should have just the first task(s) - those with no indegree
	Level n should have just the final task(s) - those with no outdegree
	"""

	# Swapping mutation
	"""
	The swapping mutation involves mixing up the execution order of two tasks.
	This requires us to make sure we are only swapping the order of tasks 
	that are independent of each other. We are lucky because in a directed graph, 
	we just need to calculate if there is a path between these nodes; if YES, then 
	we cannot swap because that breaks precedence (so we find another!).  
	"""

	random.seed(seed)
	task_order = [alloc.task.tid for alloc in solution.execution_order]

	# Calculate random ints
	order_length = len(task_order)
	selected_tasks = False
	t1, t2 = None, None
	selected_machine = random.sample(solution.machines, 1)[0]

	machine_allocations = solution.allocations[selected_machine.id]
	alloc_order = [alloc.task.tid for alloc in machine_allocations]
	alloc_length = len(machine_allocations)
	# There is the potential for an infinite loop if we have selected a machine with no swapping possible
	loop_cap = 2 * alloc_length - 1
	i = 0
	while not selected_tasks and i < loop_cap:
		i1 = random.randint(0, alloc_length - 1)
		i2 = random.randint(0, alloc_length - 1)
		if i1 > i2:
			tmp = i1
			i1 = i2
			i2 = tmp
		nodes = list(workflow.graph.nodes)
		curr_nodes = [nodes[i] for i in alloc_order]
		curr_nodes.sort(key=lambda task: alloc_order.index(task.tid))
		t1, t2 = curr_nodes[i1], curr_nodes[i2]
		i += 1
		if not nx.algorithms.shortest_paths.has_path(workflow.graph, t1, t2):
			selected_tasks = True

	if not selected_tasks:
		return None


	t1index = alloc_order.index(t1.tid)
	t2index = alloc_order.index(t2.tid)

	tmp = alloc_order[t1index]
	alloc_order[t1index] = alloc_order[t2index]
	alloc_order[t2index] = tmp

	solution_exec = solution.execution_order

	# task2 may be independent from task1, but it may need other tasks to finish before
	# it can, and therefore task 1 can. So we need to adjust the execution order accordingly.

	pred = [t.tid for t in workflow.graph.predecessors(t2)]

	for task in task_order:
		if task in pred:
			i = task_order.index(task)
			t1i = task_order.index(t1.tid)
			if i > t1i:
				task_order[t1i] = task
				task_order[i] = t1.tid
	# Now that we have ensured that none of task2 predecessors will start before it does in the eecution order,
	# we swap it with task1 to finish off the process!
	t1i = task_order.index(t1.tid)
	t2i = task_order.index(t2.tid)
	task_order[t1i] = t2.tid
	task_order[t2i] = t1.tid

	succ = [t.tid for t in workflow.graph.successors(t1)]
	for task in task_order:
		if task in succ:
			i = task_order.index(task)
			t1i = task_order.index(t1.tid)
			if i < t1i:
				task_order[t1i] = task
				task_order[i] = t1.tid
	c1 = GASolution(solution.machines)
	# c1.allocations = copy.deepcopy(solution.allocations)
	# c1.allocations[selected_machine.id].sort(key=lambda alloc: alloc_order.index(alloc.task.tid))

	# for m in solution.machines:
	# 	if m is selected_machine:
	# 		c1.allocations[selected_machine.id].sort(key=lambda alloc: alloc_order.index(alloc.task.tid))

	# for alloc in parent1.list_machine_allocations(m):
	# 	if alloc.task.tid in crossover_tasks:
	# 		continue
	# 	else:
	# 		nalloc = copy.deepcopy(alloc)
	# 		nalloc.reset()
	# 		c1_tmp_alloc.append(nalloc)

	tmp_alloc = copy.deepcopy(solution.allocations)
	tmp_alloc[selected_machine.id].sort(key=lambda alloc: alloc_order.index(alloc.task.tid))
	tmp_list = []
	for m in solution.machines:
		for alloc in tmp_alloc[m.id]:
			alloc.reset()
			tmp_list.append(alloc)
	tmp_list.sort(key=lambda alloc: task_order.index(alloc.task.tid))

	for alloc in tmp_list:
		t = alloc.task
		m = alloc.machine
		calc_start_finish_times(
			task=t,
			machine=m,
			workflow=workflow,
			curr_allocations=c1.list_machine_allocations(m),
			solution=c1
		)
		c1.add_allocation(alloc.task, alloc.machine, sort=False)
		if t.aft > c1.makespan:
			c1.makespan = t.aft

	return c1


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
			runtime = alloc.task.aft - alloc.task.ast
			cost += workflow.env.calc_task_cost_on_machine(machine, runtime)
	return cost


def generate_allocations(machines, task_order, wf, seed, solution_class=GASolution):
	soln = solution_class(machines=machines)
	rand_bounds = len(machines)
	random.seed(seed)
	for t in task_order:
		index = random.randint(0, RAND_BOUNDS) % rand_bounds
		m = machines[index]
		ast, aft = calc_start_finish_times(t, m, wf, soln.list_machine_allocations(m))
		t.ast = ast
		t.aft = aft
		solnt = copy.deepcopy(t)
		soln.add_allocation(solnt, m)
		if solnt.aft > soln.makespan:
			soln.makespan = solnt.aft

	soln.makespan = soln.execution_order[-1].task.aft
	soln.solution_cost = calc_solution_cost(soln, wf)

	return soln


def calc_start_finish_times(task, machine, workflow, curr_allocations, solution=None):
	# For a given solution, we have task-machine pairs in a given order
	# This order will be based on the execution order provided by a topological sort
	st = 0
	predecessors = workflow.graph.predecessors(task)
	for pretask in predecessors:
		solntask = pretask
		if solution:
			alloc = solution.task_allocations[pretask]
			solntask = alloc.task
		edge_comm_cost = 0
		if solntask.machine.id != machine.id:
			edge_comm_cost = workflow.graph.edges[pretask, task][WORKFLOW_DATASIZE]
		# If the finish time of the previous task is greater than st and communication cost, then we update the est
		if solntask.aft + edge_comm_cost >= st:
			st = solntask.aft + edge_comm_cost
	# Also need to check what the latest current allocation is on the machine

	num_alloc = len(curr_allocations)
	if num_alloc > 0:
		if not _check_machine_availability(workflow.solution, machine, st, task):
			final = curr_allocations[num_alloc - 1]
			# This is in the event that the task execution order places tasks
			# with the same previous task on the same machine
			if final.task.aft > st:
				st = final.task.aft

	ast = st
	runtime = task.calc_runtime(machine)
	aft = ast + runtime
	task.ast = st
	task.aft = task.ast + runtime
	task.machine = machine

	return ast, aft


def _check_machine_availability(solution, machine, start_time, task):
	for alloc in solution.list_machine_allocations(machine):
		if alloc.task.ast <= start_time < alloc.task.aft:
			return False
		# if it starts beforehand but will over-run:
		if start_time < alloc.task.ast <= start_time + task.calculated_runtime[machine]:
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
