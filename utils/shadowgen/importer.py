# /usr/bin
# Script to import a DALiuGE Physical Graph Template (PGT)

# Copyright (C) date RW Bunney

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

import os
import sys
import json
import networkx as nx

location = 'daliuge_json/'
graphs = dict()

for val in os.listdir(location):
	graphs[val] = location

for key in graphs:
	path = graphs[key] + key
	print("'Path is:" + path + "'")
	if os.path.exists(path) and (os.stat(path).st_size != 0):

		graph = dict()
		with open(path) as f:
			graph = json.load(f)

		G = nx.DiGraph()

		for val in graph:
			G.add_node(val['oid'])
			G.node[val['oid']]['nm'] = val['nm']

		for val in graph:
			if 'outputs' in val:
				for item in val['outputs']:
					G.add_edge(val['oid'], item)
			elif 'consumers' in val:
				for item in val['consumers']:
					G.add_edge(val['oid'], item)



		for node in G.nodes():
			G.node[node]['label'] = str(node)

		nx.topological_sort(G)

		variable = 'daliuge_json'
		#        if os.path.exits(variable):
		title = key.split('.')[0]
		save = variable + title
		# fname = open('{0}.graphml'.format(save),'w+')
		nx.write_graphml(G, '{0}_untranslated.graphml'.format(save))

		translate = dict()
		count = 0

		for node in nx.topological_sort(G):
			translate[node] = count
			count = count + 1

		for key, val in translate.items():
			print(str(key) + ' :' + str(val))

		translated_graph = nx.DiGraph()

		for key in translate:
			translated_graph.add_node(translate[key])

		for edge in G.edges():
			translated_graph.add_edge(translate[edge[0]], translate[edge[1]])

		for node in translated_graph.nodes():
			translated_graph.node[node]['label'] = str(node)

		variable = 'daliuge_json'
		save = variable + title
		nx.write_graphml(translated_graph, '{0}.graphml'.format(save))
