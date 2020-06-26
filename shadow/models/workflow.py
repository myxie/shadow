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


import json
import sys

import networkx as nx
import numpy as np
from shadow.models.environment import Environment
from shadow.models.solution import Solution


# TODO clean up allocation and ranking;
#  reduce direct  to the graph,
#  instead, only interact with
#  workflow tasks, naccessot graph nodes

class Task(object):
	"""
	Helper class for the
	"""

	def __init__(self, tid, flops=0):
		self.tid = tid  # task id - this is unique
		self.rank = -1  # This is updated during the 'Task Prioritisation' phase

		# Resource usage
		self.flops_demand = flops  # Will use the constants
		# Following is {machine name, value} dictionary pairs
		self.calculated_runtime = {}
		self.calculated_io = {}
		self.calculated_memory = {}

		# allocations
		self.machine = None
		self.ast = 0  # actual start time
		self.aft = 0  # actual finish time

	def __repr__(self):
		return str(self.tid)
	#
	# Node must be hashable for use with networkx
	def __hash__(self):
		return hash(self.tid)

	def __eq__(self, task):
		if isinstance(task, self.__class__):
			return self.tid == task.tid

	def __lt__(self, task):
		if isinstance(task, self.__class__):
			return self.tid < task.tid

	def __le__(self, task):
		if isinstance(task, self.__class__):
			return self.tid <= task.tid

	def calc_runtime(self, machine):
		return self.calculated_runtime[machine]

	def calc_ave_runtime(self):
		return sum(self.calculated_runtime.values()) / len(self.calculated_runtime)

	def update_task_rank(self, rank):
		self.rank = rank

	def allocate_task(self, machine_id):
		self.machine = machine_id
		pass


class Workflow(object):
	"""
	Workflow class acts as a wrapper for all things associated with a task
	workflow

	:param config: JSON formatted file that stores the structural \
	information of the underlying workflow graph. See utils.shadowgen for more \
	information on producing shadow-compatible JSON files.

	The workflow includes
	"""

	def __init__(self, config, taskobj=Task, from_file=True):
		"""
		"""
		with open(config, 'r') as infile:
			wfconfig = json.load(infile)
		self.graph = nx.readwrite.json_graph.node_link_graph(wfconfig['graph'])
		# Take advantage of how pipelines
		mapping = {}
		for node in self.graph.nodes:
			t = taskobj(node, self.graph.nodes[node]['comp'])
			mapping[node] = t
		self.graph = nx.relabel_nodes(self.graph, mapping, copy=False)
		self.tasks = self.graph.nodes
		self.edges = self.graph.edges
		self.env = None # Initialised when we 'add_environment'
		self.solution = None  # Solution is dependent on an environment
		# This lets us know when reading the graph if 'comp' attribute
		# in the Networkx graph is time or FLOPs based
		self._time = wfconfig['header']['time']

	def add_environment(self, environment):
		"""
		:param environment: An environment object using the Environment class. \
		This should be created first, then added to the Workflow.
		:return: Non-negative return value inidcates success.
		"""
		self.env = environment
		# Go through environment flags and check what processing we can do to the workflow
		self.solution = Solution(machines=[m for m in self.env.machines])
		# That is, the runtime of tasks has already been calculated
		if self._time:
			# Check the number of  values stored for each node so they match the
			# nunber of machines in thcomputatione system config
			for task in self.tasks:
				try:
					comp_array_length = len(self.tasks[task]['comp'])
				except TypeError:
					print(
						"Computation costs should be an array, but instead is {0}. Check your configuration files".format(
							self.tasks[task]['comp']
						)
					)
					raise TypeError
				if len(self.tasks[task]['comp']) is not len(self.env.machines):
					raise RuntimeError
				machines = [m for m in self.env.machines]
				runtime_list = self.tasks[task]['comp']
				task.calculated_runtime = dict(zip(machines, runtime_list))
			return 0
		# Use compute provided by system values to calculate the time taken

		else:
			for m in self.env.machines:
				for task in self.tasks:
					comp = task.flops_demand
					task.calculated_runtime[m] = int(self.env.calc_task_runtime_on_machine(m, comp))
			# self.tasks[node]['comp']
			# TODO Use rates from environment in calcuation; for the time being rates are specified in the graph

			return 0

	def sort_tasks(self, sort_type):
		"""
		Sorts task in a task wf based on a specified sort_type

		:params task_wf - Wf that has tasks to be sorted
		:params sort_type - How we sort the tasks (topological, task rank etc.)
		"""

		if sort_type == 'rank':
			return sorted(self.tasks, key=lambda x: \
				x.rank, reverse=True)

		if sort_type == 'topological':
			return nx.topological_sort(self.graph)
		else:
			raise NotImplementedError("This sorting method has not been implemented")

	def solution_exec_order(self):
		return sorted(
			self.tasks, key=lambda x: x.ast
		)

