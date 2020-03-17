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

"""
This module contais code for implementing heuristic-based scheduling
algorithms. Currently, this file implements the following algorithms:

* HEFT 
* PHEFT 
"""
from random import randint
import networkx as nx
import numpy as np
from shadow.classes.workflow import Workflow

RANDMAX = 1000

#############################################################################
############################# HUERISTICS  ###################################
#############################################################################


def heft(workflow):
	"""
	Implementation of the original 1999 HEFT algorithm.

	:params wf: The workflow object to schedule
	:returns: The makespan of the resulting schedule
	"""
	upward_rank(workflow)
	workflow.execution_order = sort_tasks(workflow, 'rank')
	makespan = insertion_policy(workflow)
	return makespan


def pheft(wf):
	"""
	Implementation of the PHEFT algorithm, which adaptst the HEFT algorithm
	using the concpet of an Optimistic Cost Table (OCT)
	"""

	oct_rank_matrix = dict()  # Necessary addition for PHEFT
	upward_oct_rank(wf, oct_rank_matrix)
	makespan = insertion_policy_oct(wf, oct_rank_matrix)
	return makespan


# TODO: Partial Critical Paths 
def pcp(wf):
	return None


# TODO: Multi-objective list scheduling
def mols(wf):
	return None


#############################################################################
############### HELPER FUNCTIONS & HEURISTIC-SPECIFIC POLICIES ##############
#############################################################################


def upward_rank(wf):
	"""
	Ranks tasks according to the specified method. Tasks need to be ranked,
	then sorted according to the rank. Returns a sorted list of tasks in
	order of rank.
	"""
	for task in sorted(list(wf.tasks)):
		rank_up(wf, task)


def upward_oct_rank(wf, oct_rank_matrix):
	for val in range(len(wf.machine_alloc)):
		for node in sorted(list(wf.tasks()), reverse=True):
			rank_oct(wf, oct_rank_matrix, node, val)

	for node in list(wf.tasks()):
		ave = 0
		for (n, p) in oct_rank_matrix:
			if n is node:
				ave += oct_rank_matrix[(n, p)]

		wf.tasks[node]['rank'] = ave / len(wf.machine_alloc)


def sort_tasks(wf, sort_type):
	"""
	Sorts task in a task wf based on a specified sort_type

	:params task_wf - Wf that has tasks to be sorted
	:params sort_type - How we sort the tasks (topological, task rank etc.)
	"""

	if sort_type == 'rank':
		return sorted(wf.tasks, key=lambda x: \
			wf.tasks[x]['rank'], reverse=True)

	if sort_type == 'topological':
		return nx.topological_sort(wf)
	else:
		return None


def rank_up(wf, task):
	"""
	Upward ranking heuristic outlined in Topcuoglu, Hariri & Wu (2002)
	Closely modelled off 'cal_up_rank' function at:
	https://github.com/oyld/heft/blob/master/src/heft.py

	Ranks individual tasks and then allocates this final value to the attribute of the workflow graph

	:param wf - Subject workflow
	:param task -  A task task in an DAG that is being ranked
	"""
	longest_rank = 0
	for successor in wf.graph.successors(task):
		if 'rank' not in wf.graph[successor]:  # if we have not assigned a rank
			rank_up(wf, successor)

		longest_rank = max(
			longest_rank, ave_comm_cost(wf, task, successor)
						+ wf.tasks[successor]['rank'])

	ave_comp = ave_comp_cost(wf, task)
	wf.tasks[task]['rank'] = ave_comp + longest_rank


def rank_up_random(wf, task):
	"""
	Computes the upward rank based on either the average, max or minimum
	computational cost
	"""

	longest_rank = 0
	for successor in wf.successors(task):
		if 'rank' not in wf.tasks[successor]:
			# if we have not assigned a rank
			rank_up(wf, successor)

		longest_rank = max(
			longest_rank, ave_comm_cost(wf, task, successor)
						+ wf.tasks[successor]['rank'])

	randval = randint(0, RANDMAX) % 3
	ave_comp = 0
	if randval is 0:
		ave_comp = ave_comp_cost(wf, task)
	elif randval is 1:
		ave_comp = max_comp_cost(wf, task)
	elif randval is 2:
		ave_comp = max_comp_cost(wf, task)

	wf.tasks[task]['rank'] = ave_comp + longest_rank


def rank_oct(wf, oct_rank_matrix, node, pk):
	"""
	Optimistic cost table ranking heuristic outlined in
	Arabnejad and Barbos (2014)
	"""
	max_successor = 0
	for successor in wf.graph.successors(node):
		min_processor = 1000
		for processor in range(0, len(wf.machine_alloc)):
			oct_val = 0
			if (successor, processor) not in oct_rank_matrix.keys():
				rank_oct(wf, oct_rank_matrix, successor, processor)
			comm_cost = 0
			comp_cost = wf.tasks[successor]['comp'][processor]
			if processor is not pk:
				comm_cost = ave_comm_cost(wf, node, successor)
			oct_val = oct_rank_matrix[(successor, processor)] + \
					  comp_cost + comm_cost
			min_processor = min(min_processor, oct_val)
		max_successor = max(max_successor, min_processor)

	oct_rank_matrix[(node, pk)] = max_successor


def ave_comm_cost(wf, task, successor):
	"""
	Returns the 'average' communication cost, which is just
	the cost in the matrix. Not sure how the ave. in the
	original paper was calculate or represented...

	:params task: Starting task
	:params successor: Node with which the starting task is communicating
	"""
	# TODO sort out data rates in future release
	# cost, zeros = 0, 0
	# data_product_size = wf.graph.edges[task, successor]['data_size']
	# for val in range(len(wf.system['data_rate'][0])):
	# 	rate = wf.system['data_rate'][0][val]
	# 	if rate != 0:
	# 		cost += data_product_size / rate
	# 	else:
	# 		zeros += 1
	# denominator = len(wf.system['data_rate'][0]) - zeros
	#
	# # if denominator is 0, the data rate between each machine is negligible.
	# if denominator == 0:
	# 	return 0
	# else:
	# 	return int(cost / denominator)

	return wf.graph.edges[task, successor]['data_size']


def ave_comp_cost(wf, task):
	comp = wf.tasks[task]['comp']
	return sum(comp) / len(comp)


def max_comp_cost(wf, task):
	comp = wf.tasks[task]['comp']
	return max(comp)


def min_comp_cost(wf, task):
	comp = wf.tasks[task]['comp']
	return min(comp)


def calc_est(wf, task, machine):
	"""
	Calculate the Estimated Start Time of a task on a given processor
	"""

	est = 0
	predecessors = wf.graph.predecessors(task)
	for pretask in predecessors:
		if 'processor' not in wf.tasks[pretask]:
			wf.tasks[pretask]['processor'] = None  # Default to 0
		# If task isn't on the same processor, there is a transfer cost
		pre_processor = wf.tasks[pretask]['processor']
		# rate = wf.system['data_rate'][pre_processor][machine]
		if pre_processor != machine:  # and rate > 0:
			comm_cost = int(wf.graph.edges[pretask, task]['data_size'])  # / rate)
		else:
			comm_cost = 0

		# wf.graph.predecessors is not being updated in insertion_policy;
		# need to use the tasks that are being updated to get the right results
		# index = task_list.index(pretask)
		# print(pretask)
		aft = wf.tasks[pretask]['aft']
		tmp = aft + comm_cost
		if tmp >= est:
			est = tmp

	machine_str = list(wf.machine_alloc.keys())[machine]
	machine_allocs = wf.machine_alloc[machine_str]
	# Structure of our processor allocation is
	# [{id:, ast:, aft:},{id:, ast:, aft:}]
	# Now we find the time it fits in on the processor
	# processor = wf.machine_alloc[machine]  # return the list of allocated tasks
	available_slots = []
	prev = None
	if len(machine_allocs) == 0:
		return est  # Nothing in the time slots yet
	else:
		for i in range(len(machine_allocs)):
			# For each start/finish time tuple that exists in the processor
			if i == 0:
				if machine_allocs[i]['ast'] != 0:  # If the start time of the first tuple is not 0
					available_slots.append((0, machine_allocs[i]['ast']))  # add a 0-current_start time tuple
				else:
					continue
			else:
				# Append the finish time of the previous slot and the ostart time of this slot
				prev_allocation = machine_allocs[i - 1]
				available_slots.append((machine_allocs[i - 1]['aft'], machine_allocs[i]['ast']))

		# Add a -1 to the final time slot available, so we have a 'gap' after
		final_alloc = machine_allocs[len(machine_allocs) - 1]
		available_slots.append((final_alloc['aft'], -1))

	for slot in available_slots:
		if est < slot[0] and slot[0] + \
				wf.tasks[task]['comp'][machine] <= slot[1]:
			return slot[0]
		if (est >= slot[0]) and \
				(est +
				 wf.tasks[task]['comp'][machine] <= slot[1]):
			return est
		# At the 'end' of available slots
		if (est >= slot[0]) and (slot[1] < 0):
			return est
		# This last case occurs when we have a low est but a high cost, so
		# it doesn't fit in any gaps; hence we have to put it at the 'end'
		# and start it late
		if (est < slot[0]) and (slot[1] < 0):
			return slot[0]

	return est

more test
def insertion_policy(wf):
	"""
	Allocate tasks to machines following the insertion based policy outline
	in Tocuoglu et al.(2002)
	"""
	makespan = 0
	tasks = sort_tasks(wf, 'rank')
	for task in tasks:
		if task == tasks[0]:
			w = min(wf.tasks[task]['comp'])
			p = list(wf.tasks[task]['comp']).index(w)
			# 'p' is the index of machine_alloc.keys() we want
			wf.tasks[task]['processor'] = p
			wf.tasks[task]['ast'] = 0
			wf.tasks[task]['aft'] = w
			machine_str = list(wf.machine_alloc.keys())[p]
			wf.machine_alloc[machine_str].append({
				"id": task,
				"ast": wf.tasks[task]['ast'],
				"aft": wf.tasks[task]['aft']
			})
		else:
			aft = -1  # Finish time for the current task
			p = 0
			for processor in range(len(wf.machine_alloc)):
				# tasks in self.rank_sort are being updated, not wf.graph;
				est = calc_est(wf, task, processor)
				if aft == -1:  # assign initial value of aft for this task
					aft = est + wf.tasks[task]['comp'][processor]
					p = processor
				# see if the next processor gives us an earlier finish time
				elif est + wf.tasks[task]['comp'][processor] < aft:
					aft = est + wf.tasks[task]['comp'][processor]
					p = processor

			wf.tasks[task]['processor'] = p
			wf.tasks[task]['ast'] = aft - wf.tasks[task]['comp'][p]
			wf.tasks[task]['aft'] = aft

			if wf.tasks[task]['aft'] >= makespan:
				makespan = wf.tasks[task]['aft']
			machine_str = list(wf.machine_alloc.keys())[p]
			wf.machine_alloc[machine_str].append({
				"id": task,
				"ast": wf.tasks[task]['ast'],
				"aft": wf.tasks[task]['aft'],
			})
			wf.machine_alloc[machine_str].sort(key=lambda x: x['ast'])

	wf.makespan = makespan
	return makespan


def insertion_policy_oct(wf, oct_rank_matrix):
	"""
	Allocate tasks to machines following the insertion based policy outline
	in Tocuoglu et al.(2002)
	"""

	makespan = 0
	if not oct_rank_matrix:
		upward_oct_rank(wf, oct_rank_matrix)
	eft_matrix = dict()
	oeft_matrix = dict()
	p = 0
	tasks = sort_tasks(wf, 'rank')
	for task in tasks:
		if task == tasks[0]:
			wf.tasks[task]['ast'] = 0
			min_oeft = -1
			for processor in range(len(wf.machine_alloc)):
				eft_matrix[(task, processor)] = wf.tasks[task]['comp'][processor]
				oeft_matrix[(task, processor)] = \
					eft_matrix[(task, processor)] + oct_rank_matrix[(task, processor)]
				if (min_oeft == -1) or \
						(oeft_matrix[(task, processor)] < min_oeft):
					min_oeft = oeft_matrix[(task, processor)]
					p = processor
			wf.tasks[task]['aft'] = wf.tasks[task]['comp'][p]
			wf.tasks[task]['processor'] = p
			machine_str = list(wf.machine_alloc.keys())[p]
			wf.machine_alloc[machine_str].append({
				"id": task,
				"ast": wf.tasks[task]['ast'],
				"aft": wf.tasks[task]['aft'],
			})

		else:
			min_oeft = -1
			for processor in range(len(wf.machine_alloc)):
				if wf.graph.predecessors(task):
					est = calc_est(wf, task, processor)
				else:
					est = 0
				eft = est + wf.tasks[task]['comp'][processor]
				eft_matrix[(task, processor)] = eft
				oeft_matrix[(task, processor)] = \
					eft_matrix[(task, processor)] + oct_rank_matrix[(task, processor)]
				if (min_oeft == -1) or \
						(oeft_matrix[(task, processor)] < min_oeft):
					min_oeft = oeft_matrix[(task, processor)]
					p = processor

			wf.tasks[task]['aft'] = eft_matrix[(task, p)]

			wf.tasks[task]['ast'] = \
				wf.tasks[task]['aft'] \
				- wf.tasks[task]['comp'][p]

			wf.tasks[task]['processor'] = p

			if wf.tasks[task]['aft'] >= makespan:
				makespan = wf.tasks[task]['aft']

			machine_str = list(wf.machine_alloc.keys())[p]
			wf.machine_alloc[machine_str].append({
				"id": task,
				"ast": wf.tasks[task]['ast'],
				"aft": wf.tasks[task]['aft'],
			})
			wf.machine_alloc[machine_str].sort(key=lambda x: x['ast'])

	wf.makespan = makespan
	return makespan
