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
import matplotlib.pyplot as plt
from shadow.classes.environment import Environment


# TODO clean up allocation and ranking;
#  reduce direct  to the graph,
#  instead, only interact with
#  workflow tasks, naccessot graph nodes


class Workflow(object):
	"""
	Workflow class acts as a wrapper for all things associated with a task
	workflow

	:param config: JSON formatted file that stores the structural \
	information of the underlying workflow graph. See utils.shadowgen for more \
	information on producing shadow-compatible JSON files.
	"""

	def __init__(self, config):
		"""
		"""
		with open(config, 'r') as infile:
			wfconfig = json.load(infile)
		self.graph = nx.readwrite.json_graph.node_link_graph(wfconfig['graph'])
		# Take advantage of how pipelines
		self.tasks = self.graph.nodes
		self.edges = self.graph.edges
		self.env = None
		self.machine_alloc = {}
		self.execution_order = []
		# This lets us know when reading the graph if 'comp' attribute
		# in the Networkx graph is time or FLOPs based
		self._time = wfconfig['header']['time']

	class Task(object):
		"""
		Task class designed to reduce the reliance on dictionary access in the workflow class
		"""
		def __init__(self, tid):
			pass

	def add_environment(self, environment):
		"""
		:param environment: An environment object using the Environment class. \
		This should be created first, then added to the Workflow.
		:return: Non-negative return value inidcates success.
		"""
		self.env = environment
		# Go through environment flags and check what processing we can do to the workflow
		self.machine_alloc = {m: [] for m in self.env.machines.keys()}
		if self._time:
			# Check the number of computation values stored for each node so they match the
			# nunber of machines in the system config
			for node in self.tasks:
				if len(self.tasks[node]['comp']) is not self.env.num_machines:
					return -1
				if 'calculated_runtime' not in self.tasks[node]:
					self.tasks[node]['calculated_runtime'] = {}
				machines = self.env.machines.keys()
				runtime_list = self.tasks[node]['comp']
				self.tasks[node]['calculated_runtime'] = dict(zip(machines, runtime_list))
			# sys.exit("Number of machines defined in environment is"
			# 	  "not equivalent to the number definited in the workflow graph")
			return 0
		if self.env.has_comp:
			# Use compute provided by system values to calculate the time taken
			provided_flops = []
			for m in self.env.machines:
				for node in self.tasks:
					if 'calculated_runtime' not in self.tasks[node]:
						self.tasks[node]['calculated_runtime'] = {}
					comp = self.tasks[node]['comp']
					self.tasks[node]['calculated_runtime'][m] = int(comp / self.env.machines[m]['flops'])
			# self.tasks[node]['comp']
			# TODO Use rates from environment in calcuation; for the time being rates are specified in the graph

			return 0

	def calc_ave_runtime(self, task):
		runtime = self.tasks[task]['calculated_runtime'].values()
		return sum(runtime)/len(runtime)

	def update_task_rank(self, task, rank):
		self.tasks[task]['rank'] = rank

	def allocate_task(self, task, machine_id):
		pass

	pass


	def sort_tasks(self, sort_type):
		"""
		Sorts task in a task wf based on a specified sort_type

		:params task_wf - Wf that has tasks to be sorted
		:params sort_type - How we sort the tasks (topological, task rank etc.)
		"""

		if sort_type == 'rank':
			return sorted(self.tasks, key=lambda x: \
				self.tasks[x]['rank'], reverse=True)

		if sort_type == 'topological':
			return nx.topological_sort(self)
		else:
			return None

	def pretty_print_allocation(self):
		print(json.dumps(self.machine_alloc, indent=2))



