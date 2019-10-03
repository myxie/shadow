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

import numpy as np
import networkx as nx


def generate_system_machines(config_path, num_machines, magnitude='giga', heterogeneity=[1.0], specrange=[(10, 20)]):
	# TODO move the necessary information from generate_graph_costs here for system configuration
	"""
	:param num_machines:
	:param magnitude:
	:param heterogeneity:
	:param specrange: List of ranges of FLOP/s provided by each separate machine (aligns with heterogeneity list),
	relative to specified magnitude
	:return:
	"""
	multiplier = 1  # default is Giga flops
	max_data_rate = 10  # (10 Gigabytes/sec)
	if magnitude is 'giga':
		pass
	elif magnitude is 'tera':
		multiplier *= 10
	elif magnitude is 'peta':
		multiplier *= 10 * 10
	else:
		print('Provided magnitude', magnitude, 'is not supported')
		sys.exit()

	if sum(heterogeneity) != 1:
		sys.exit('System heterogeneity does not sum to 100%!')
	heterogeneity = np.array(heterogeneity)

	if len(specrange) != len(heterogeneity):
		sys.exit('FLOP/s range list provided does not match heterogeneity (List is wrong size)')

	machines = []
	for p in heterogeneity:
		tmp = num_machines * p
		machines.append(tmp)

	for m in machines:
		if 0 < np.remainder(m, 1) < 1:
			sys.exit('Number of machines specified ({0}) and percentage split on systerm ({1}) not compatible'.format(
				num_machines, heterogeneity
			))

	machine_categ = {}
	y = 0
	for i, m in enumerate(machines):
		# nd = int(random.uniform(10, 20))
		lwr, upr = specrange[i][0], specrange[i][1]
		rnd = random.uniform(lwr * multiplier, upr * multiplier)
		# TODO rewrite this as a for loop for each machine category, add a new machine
		# machine_categ['cat{0}'.format(i)] = {}
		for x in range(int(m)):
			machine_categ['cat{0}_m{1}'.format(i, y)] = {'flops': rnd - (rnd % multiplier)}
			y += 1

	data_rates = {}
	for i in range(len(heterogeneity)):
		rnd = random.uniform(1, max_data_rate)
		data_rates['cat{0}'.format(i)] = rnd - (rnd % multiplier)

	system = {
		"header": {
			"time": 'false'
		},
		'system':
			{
				'resources': machine_categ,
				'rates': data_rates
			}
	}

	with open(config_path, 'w+') as jfile:
		json.dump(system, jfile, indent=2)


# data_rate_matrix = []
# for x in range(num_machines):
# 	row = [1 for y in range(num_machines)]
# 	row[x] = 0
# 	data_rate_matrix.append(row)
#
# system = {'resource': [random.randint(0, 20) for x in range(num_machines)],
# 		  'data_rate': data_rate_matrix}
# jgraph['system'] = system

def generate_graph_costs(dot_path, json_path, ccr, mean, uniform_range, magnitude='giga'):
	"""
	:param heterogeneity:
	:param magnitude:
	:param dot_path: The path of the dot file for which we are generating cost values
	:param ccr: Communication/Computation cost ratio
	:param mean: The mean value for out uniform distribution
	:param uniform_range: the range above/below the mean for the uniform distribution
	:param num_machines: The number of machines that are in the system on which we are scheduling
	:param json_path: If specified, use this path as output for json
	:return: None
	"""
	os.listdir('.')
	print(dot_path)
	multiplier = 1  # default is Giga flops
	if magnitude is 'giga':
		pass
	elif magnitude is 'tera':
		multiplier *= 10
	elif magnitude is 'peta':
		multiplier *= 10 * 10
	else:
		print('Provided magnitude', magnitude, 'is not supported')
		sys.exit()

	# Use networkx to read in graph from DOT format and convert to JSON
	dotgraph = nx.convert_node_labels_to_integers(
		nx.DiGraph(nx.drawing.nx_pydot.read_dot(dot_path))
	)

	# Generate 'comp-FLOPs' and 'machine FLOP/s' values for the graph with given CCR
	comp_min = (mean - uniform_range) * multiplier
	comp_max = (mean + uniform_range) * multiplier

	# check heterogeneity sum is 100 (this list represents the percentage of the total cluster
	# is made of a particular machine type, where 'type' --> machine of particular FLOPS
	# total = 0
	# for x in range(num_machines):
	# 	total += heterogeneity[(x % len(heterogeneity))]
	# Generate machine cost values

	for node in dotgraph:
		rnd = int(random.uniform(comp_min, comp_max))
		dotgraph.node[node]['total_flop'] = rnd - (rnd % multiplier)

	# Generate data loads between edges and data-link transfer rates
	comm_mean = int(mean * ccr)
	comm_min = (comm_mean - (uniform_range * ccr)) * multiplier
	comm_max = (comm_mean + (uniform_range * ccr)) * multiplier
	for edge in dotgraph.edges:
		rnd = int(random.uniform(comm_min, comm_max))
		dotgraph.edges[edge]['data_size'] = rnd - (rnd % multiplier)

	jgraph = {'graph': nx.readwrite.node_link_data(dotgraph)}
	# Generate place holder system values (resources/data_rate) for compatibility with shadow library format

	if not json_path:
		json_path = '{0}.json'.format(dot_path[:-4])
	with open(json_path, 'w') as jfile:
		json.dump(jgraph, jfile, indent=2)


if __name__ == '__main__':
	args = sys.argv
	print(args)
	if len(args) > 1:
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
		for path in sorted(os.listdir('test/')):
			if 'dot' in path:
				print(os.listdir('test/.'))
				print('Generating json for test/{0}'.format(path))
				generate_graph_costs('test/{0}'.format(path), 'test/json/{0}.json'.format(path[:-4]),
									 1, 100, 50, 'giga')
				generate_system_machines('test/json/{}_sys.json'.format(path[:-4]),
										 4, 'giga', [0.5, 0.5], [(10, 20), (5, 10)])
