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
#  reduce direct access to the graph,
#  instead, only interact with
#  workflow tasks, not graph nodes


class Workflow(object):
	"""
	Workflow class acts as a wrapper for all things associated with a task
	workflow. A workflow object is a struct to keep associated data
	together.
	"""

	def __init__(self, wfdesc):
		"""
		"""
		with open(wfdesc, 'r') as infile:
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

	def add_environment(self, environment):
		self.env = environment
		# Go through environment flags and check what processing we can do to the workflow
		self.machine_alloc = {m: [] for m in self.env.machines.keys()}
		if self._time:
			# Check the number of computation values stored for each node so they match the
			# nunber of machines in the system config
			for node in self.tasks:
				if len(self.tasks[node]['comp']) is not self.env.num_machines:
					return -1
				# sys.exit("Number of machines defined in environment is"
				# 	  "not equivalent to the number definited in the workflow graph")
				else:
					return 0
		if self.env.has_comp:
			# Use compute provided by system values to calculate the time taken
			provided_flops = []
			for m in self.env.machines:
				provided_flops.append(self.env.machines[m]['flops'])
			for node in self.tasks:
				n = self.env.num_machines
				comp = self.tasks[node]['comp']
				self.tasks[node]['flops'] = self.tasks[node]['comp']
				base_comp_matrix = np.array([comp for x in range(n)])
				runtime_array = np.round(np.divide(base_comp_matrix, provided_flops)).astype(int)
				# self.tasks[node]['comp']
			# TODO Use rates from environment in calcuation; for the time being rates are specified in the graph

		return 0

	def add_rank(self, node, rank):
		pass

	def allocate_task(self, task, machine_id):
		pass

	def pretty_print_allocation(self):
		print(json.dumps(self.machine_alloc, indent=2))


