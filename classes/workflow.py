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

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


class Workflow(object):
	"""
	Workflow class acts as a wrapper for all things associated with a task
	workflow. A workflow object is a struct to keep associated data
	together.
	"""

	def __init__(self, json_file, calc_time=True):
		"""
		:params wcost - work cost matrix
		:paramts ccost - communication cost matrix
		:graphml - graphml file in which workflows are stored
		"""
		# TODO No more graphml format for us! Move to new multi-dictionary json format
		#: Initialised from graphml file

		with open(json_file, 'r') as infile:
			jgraph = json.load(infile)
		self.graph = nx.readwrite.json_graph.node_link_graph(jgraph['graph'])
		# self.graph = nx.read_graphml(graphml, int)
		self.system = jgraph['system']
		# wcost, resource_vec = [], []
		# data_size = {}
		# data_rate = []
		# TODO None of this should need to change?

		# graph.node[node_id] -> {'comp':119}
		# graph.edge[node1,node2] -> {'data_size':9}

		if calc_time:
			for node in self.graph.node:
				self.graph.node[node]['comp'] = np.round(np.divide(self.graph.node[node]['comp'], self.system['resource'])).astype(int)
			# TODO implement second data approach, which takes the rate of transfer
			#  between resources and calculates time based on that.
			# for edge in self.graph.edges:
			# 	pred, succ = edge[0], edge[1]
			# 	self.graph.edges[pred, succ]['data_size'] = data_size[str(pred)][succ]

		self.processors = [[] for x in range(len(self.system['resource']))]
		self.makespan = 0
		# self.data_rate = data_rate
		self.data_load = np.array([])
		self.thrpt = 0.0

	def top_sorts(self):
		return nx.all_topological_sorts(self.graph)

	def pretty_print_allocation(self):

		for p in self.processors:
			p = sorted(p)
		# print(p)
		print()

		for x in range(len(list(self.graph.nodes))):
			print(x, end='\t')
			tabstop = ""
			for p in range(len(self.processors)):
				if x < len(self.processors[p]):
					print("{0}".format(self.processors[p][x]), end='\t')
				else:
					tabstop = '\t\t'
					print(tabstop, end='')
			print()

		print("Total Makespan: {0}".format(self.makespan))

		self.thrpt = np.average(self.data_load)

		fig, ax1 = plt.subplots()
		ax1.plot(self.data_load)
		ax1.set_xlabel("Time (sec)")
		ax1.set_ylabel("Data Load in Pipeline (Gb)")

		val = 0
		for x, edge in enumerate(self.graph.edges):
			pred, succ = edge[0], edge[1]
			val += self.graph.edges[pred, succ]['data_size']

		ave_throughput = np.gradient(self.data_load)
		# ave_throughput = [val/self.makespan for x in range(self.makespan)]
		# ax2 = ax1.twinx()
		ax1.plot(ave_throughput, 'r')
		# ax1.plot(cumulative,'r')
		# ax2.set_ylabel("Throughput (Gb/s)", color='r')
		# ax2.tick_params('y', colors='r')
		# plt.legend((p1[0],p2[0]),('Instantaneous Load','Average Throughput'),loc=4)
		plt.title("Data load experienced over workflow vs. Rate of change of Throughput")
		plt.show()

# fig, ax1 = plt.subplots()
# t = np.arange(0.01, 10.0, 0.01)
# s1 = np.exp(t)
# ax1.plot(t, s1, 'b-')
# ax1.set_xlabel('time (s)')
# # Make the y-axis label, ticks and tick labels match the line color.
# ax1.set_ylabel('exp', color='b')
# ax1.tick_params('y', colors='b')

# ax2 = ax1.twinx()
# s2 = np.sin(2 * np.pi * t)
# ax2.plot(t, s2, 'r.')
# ax2.set_ylabel('sin', color='r')
# ax2.tick_params('y', colors='r')

# fig.tight_layout()
# plt.show()
