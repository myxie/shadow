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
import random
import sys
import os
import subprocess
import networkx as nx


def generate_graph_costs(dot_path, ccr, mean, uniform_range, num_machines, json_path=None):
	"""
	:param dot_path: The path of the dot file for which we are generating cost values
	:param ccr: Communication/Computation cost ratio
	:param mean: The mean value for out uniform distribution
	:param uniform_range: the range above/below the mean for the uniform distribution
	:param num_machines: The number of machines that are in the system on which we are scheduling
	:param json_path: If specified, use this path as output for json
	:return: None
	"""

	# Use networkx to read in graph from DOT format and convert to JSON
	dotgraph = nx.convert_node_labels_to_integers(
		nx.DiGraph(nx.drawing.nx_pydot.read_dot(dot_path)))

	# Generate 'comp' and 'data_size' values for the graph with given CCR
	comp_min = mean - uniform_range
	comp_max = mean + uniform_range

	comm_mean = int(mean*ccr)
	comm_min = comm_mean - (uniform_range*ccr)
	comm_max = comm_mean + (uniform_range*ccr)

	for node in dotgraph:
		cost_list = []
		for p in range(num_machines):
			cost_list.append(int(random.uniform(comp_min, comp_max)))
		dotgraph.node[node]['comp'] = cost_list
	for edge in dotgraph.edges:
		dotgraph.edges[edge]['data_size'] = int(random.uniform(comm_min, comm_max))

	jgraph = {'graph': nx.readwrite.node_link_data(dotgraph)}
	# Generate place holder system values (resources/data_rate) for compatibility with shadow library format

	data_rate_matrix = []
	for x in range(num_machines):
		row = [1 for y in range(num_machines)]
		row[x] = 0
		data_rate_matrix.append(row)

	system = {'resource': [random.randint(0, 20) for x in range(num_machines)],
						'data_rate': data_rate_matrix }
	jgraph['system'] = system
	if not json_path:
		json_path = '{0}.json'.format(dot_path[:-4])
	with open(json_path, 'w') as jfile:
		json.dump(jgraph, jfile, indent=2)


if __name__ == '__main__':
	args = sys.argv
	print(args)
	if args[1] == 'ggen':
		print("Using Ggen graph generating library")

		'''
		Here, we loop through the range provided on the command line
		'''
		increment = 2
		min = int(args[2])
		max = int(args[3])
		# prob = float(args[4])
		# increment = int(args[5])

		for x in range(min, max, increment):
			outfile = 'dots/ggen_out_{0}-denselu.dot'.format(x)
			print('Generating file: {0}'.format(outfile))
			subprocess.run(['ggen', '-o', '{0}'.format(outfile), 'dataflow-graph', 'denselu', str(x)])

	else:
		print('Generating json')
		for path in sorted(os.listdir('.')):
			if 'dot' in path:
				print('Generating json for{0}'.format(path))
				generate_graph_costs('{0}'.format(path), 1, 100, 50, 3)

