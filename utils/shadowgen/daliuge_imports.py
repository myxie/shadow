# Copyright (C) 5/2/20 RW Bunney

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
import os
import subprocess
import networkx as nx
import random
from networkx.drawing.nx_pydot import write_dot
EAGLE_GRAPH = 'daliuge_graphs/TestAskapCont.graph'
CHANNELS = 10 
SEED = 20
MEAN = 5000
UNIFORM_RANGE = 500
MULTIPLIER = 1
CCR = 0.5

random.seed(SEED)
# EDIT THE EAGLE GRAPH TO CHANGE THE NUMBER OF CHANNELS
f = open(EAGLE_GRAPH, 'r')
jdict = json.load(f)
f.close()
jdict['nodeDataArray'][0]['fields'][0]['value'] = CHANNELS

ngraph = "{0}_channels-{1}.graph".format(EAGLE_GRAPH[:-6], CHANNELS)
f = open(ngraph, 'w')
json.dump(jdict,f, indent=2)
f.close()
# UNROLL THE GRAPH 
if os.path.exists(ngraph):
	print(ngraph)
	
	cmd_list = ['dlg', 'unroll-and-partition', '-fv', '-L', ngraph]
	jgraph_path = "{0}.json".format(ngraph[:-6])
	with open(format(jgraph_path), 'w+') as f:
		subprocess.call(cmd_list, stdout=f)
else:
	print("Failure to find path {0}".format(ngraph))
location = 'daliuge_json/'
graphs = dict()


path = jgraph_path 
print("'Path is:" + path + "'")
# READ IN UNROLLED GRAPH AND ADD THE COMPUTATION VALUES
if os.path.exists(path) and (os.stat(path).st_size != 0):
	
	with open(path) as f:
		graphdict = json.load(f)

	G = nx.DiGraph()

	for val in graphdict:
		if 'app' in val.keys():
			if val['app'] == "dlg.apps.simple.SleepApp":
				continue
		G.add_node(val['oid'])
		G.nodes[val['oid']]['nm'] = val['nm']

	for val in graphdict:
		if 'app' in val.keys():
			if val['app'] == "dlg.apps.simple.SleepApp":
				continue
		if 'outputs' in val:
			for item in val['outputs']:
				G.add_edge(val['oid'], item)
		elif 'consumers' in val:
			for item in val['consumers']:
				G.add_edge(val['oid'], item)

	for node in G.nodes():
		G.nodes[node]['label'] = str(node)

	translate = {}
	count = 0

	for node in nx.topological_sort(G):
		translate[node] = count
		count = count + 1

	for key, val in translate.items():
		print(str(key) + ' :' + str(val))

	translated_graph = G # nx.DiGraph()

	# for key in translate:
	# 	translated_graph.add_node(translate[key])
	#
	# for edge in G.edges():
	# 	translated_graph.add_edge(translate[edge[0]], translate[edge[1]])
	#
	# for node in translated_graph.nodes():
	# 	translated_graph.nodes[node]['label'] = str(node)
		
	comp_min = (MEAN - UNIFORM_RANGE) * MULTIPLIER
	comp_max = (MEAN + UNIFORM_RANGE) * MULTIPLIER

	# check heterogeneity sum is 100 (this list represents the percentage of the total cluster
	# is made of a particular machine type, where 'type' --> machine of particular FLOPS
	# total = 0
	# for x in range(num_machines):
	# 	total += heterogeneity[(x % len(heterogeneity))]
	# Generate machine cost values

	for node in translated_graph:
		rnd = int(random.uniform(comp_min, comp_max))
		translated_graph.nodes[node]['comp'] = rnd - (rnd % MULTIPLIER)

	# Generate data loads between edges and data-link transfer rates
	comm_mean = int(MEAN * CCR)
	comm_min = (comm_mean - (UNIFORM_RANGE * CCR)) * MULTIPLIER
	comm_max = (comm_mean + (UNIFORM_RANGE * CCR)) * MULTIPLIER
	for edge in translated_graph.edges:
		rnd = int(random.uniform(comm_min, comm_max))
		translated_graph.edges[edge]['data_size'] = rnd - (rnd % MULTIPLIER)

	jgraph = {
		"header": {
			"time": False
		},
		'graph': nx.readwrite.node_link_data(translated_graph)
	}
	# Generate place holder system values (resources/data_rate) for compatibility with shadow library format
	write_dot(translated_graph, "dot.dot")
	# if not json_path:
	# 	json_path = '{0}.json'.format(dot_path[:-4])
	# with open(json_path, 'w') as jfile:
	# 	json.dump(jgraph, jfile, indent=2)
	
	save = "{0}_shadow.json".format(path[:-5])
	with open("{0}.json".format(save), 'w') as jfile:
		json.dump(jgraph, jfile, indent=2)
