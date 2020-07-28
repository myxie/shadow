# Copyright (C) 10/2/20 RW Bunney

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
import subprocess
import os
import json
import sys
import datetime
import random

import networkx as nx

import utils.shadowgen.generator as generator

EAGLE_EXT = ".input"
EAGLE_GRAPH = 'test/data/shadowgen/SDPContinuumPipelineNoOuter.input'
CHANNELS = 10
CHANNEL_SUFFIX = "_channels-{0}".format(CHANNELS)
SEED = 20
MEAN = 5000
UNIFORM_RANGE = 500
MULTIPLIER = 1
CCR = 0.5


def edit_channels(graph_name, suffix, extension):
	f = open(graph_name, 'r')
	jdict = json.load(f)
	f.close()
	# TODO make this less hard-coded?
	jdict['nodeDataArray'][0]['fields'][0]['value'] = CHANNELS
	ngraph = graph_name[:-6] + suffix + extension
	f = open(ngraph, 'w')
	json.dump(jdict, f, indent=2)
	f.close()
	return ngraph


def unroll_logical_graph(graph):
	cmd_list = ['dlg', 'unroll-and-partition', '-fv', '-a', 'mysarkar', '-L', graph]
	jgraph_path = "{0}.json".format(graph[:-6])
	with open(format(jgraph_path), 'w+') as f:
		subprocess.call(cmd_list, stdout=f)
	return jgraph_path


def generate_dot_from_networkx_graph(graph, output):
	dot_path = "{0}.dot".format(output)
	nx.drawing.nx_pydot.write_dot(graph, dot_path)
	cmd_list = [
		'dot',
		'-Tpdf',
		'{0}.dot'.format(output)
	]

	dot_pdf = "{0}.pdf".format(output)
	with open(dot_pdf, 'w') as f:
		subprocess.call(cmd_list, stdout=f)
		return dot_path


def json_to_shadow(
		daliuge_json,
		output_file,
		mean,
		uniform_range,
		multiplier,
		ccr,
		seed=20):
	"""
	Daliuge import will use
	:return:
	"""
	random.seed(seed)
	if os.path.exists(daliuge_json) and (os.stat(daliuge_json).st_size != 0):

		with open(daliuge_json) as f:
			graphdict = json.load(f)

		# Storing the nodes and edges from the unrolled DALiuGE input
		unrolled_nx = nx.DiGraph()

		# There is something about this simple.SleepApp that is a bug in the old DALiuGE Translator
		for val in graphdict:
			if 'app' in val.keys():
				if val['app'] == "dlg.apps.simple.SleepApp":
					continue
			unrolled_nx.add_node(val['oid'])
			unrolled_nx.nodes[val['oid']]['nm'] = val['nm']

		for val in graphdict:
			if 'app' in val.keys():
				if val['app'] == "dlg.apps.simple.SleepApp":
					continue
			if 'outputs' in val:
				for item in val['outputs']:
					unrolled_nx.add_edge(val['oid'], item)
			elif 'consumers' in val:
				for item in val['consumers']:
					unrolled_nx.add_edge(val['oid'], item)

		comp_dict = generator.generate_comp_costs(
			unrolled_nx.nodes, mean, uniform_range, multiplier
		)

		for node in unrolled_nx.nodes():
			unrolled_nx.nodes[node]['label'] = unrolled_nx.nodes[node]['nm']
			unrolled_nx.nodes[node]['flops'] = comp_dict[node]

		edge_dict = generator.genereate_data_costs(
			unrolled_nx.edges,mean,uniform_range,multiplier,ccr
		)

		for edge in unrolled_nx.edges():
			unrolled_nx.edges[edge]['data_size'] = edge_dict[edge]

		translation_dict = {}
		count = 0

		for node in nx.topological_sort(unrolled_nx):
			translation_dict[node] = count
			count = count + 1

		for key, val in translation_dict.items():
			print(str(key) + ' :' + str(val))

		translated_graph = nx.DiGraph()
		for key in translation_dict:
			translated_graph.add_node(translation_dict[key])

		for edge in unrolled_nx.edges():
			(u,v) = edge
			translated_graph.add_edge(translation_dict[u], translation_dict[v])

		for node in translated_graph.nodes():
			translated_graph.nodes[node]['label'] = str(node)
			translated_graph.nodes[node]['comp'] = unrolled_nx.nodes[node]['flops']

		# Generate data loads between edges and data-link transfer rates

		for edge in translated_graph.edges:
			translated_graph.edges[edge]['data_size'] = unrolled_nx.nodes[edge]['data_size']

		jgraph = {
			"header": {
				"time": False,
				"gen_specs":{
					'file':daliuge_json,
					'mean': mean,
					'range':"+{0}".format(uniform_range),
					'seed': seed,
					'ccr':ccr,
					'multiplier':multiplier
				},
			},
			'input': nx.readwrite.node_link_data(translated_graph)
		}

		with open("{0}".format(output_file), 'w') as jfile:
			json.dump(jgraph, jfile, indent=2)
		return unrolled_nx, output_file


if __name__ == '__main__':
	# edited_graph = edit_channels(EAGLE_GRAPH, CHANNEL_SUFFIX, EAGLE_EXT)
	unrolled_graph = unroll_logical_graph(EAGLE_GRAPH)
	nxgraph = json_to_shadow(unrolled_graph,'output.json', MEAN, UNIFORM_RANGE, MULTIPLIER, CCR)
	retval = generate_dot_from_networkx_graph(nxgraph, 'output')
