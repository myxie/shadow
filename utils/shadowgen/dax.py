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

import xml.etree.ElementTree as et
from networkx.readwrite import json_graph
import json
import networkx as nx
import sys


## NB DAX Data values are measured in BYTES. This is why they are (perhaps unnecessarily) large

# allows for removal of string which interferes with etree
def clean_xml(filename, newfile, search_str, replacement_str):
	edited_str_lines = []
	with open(filename, 'r') as infile:
		for line in infile:
			# output of searchString method is the index of said str or
			# -1 if the search_str is not present
			if line.find(search_str) >= 0:
				edited_str_lines.append(replacement_str)
			else:
				edited_str_lines.append(line)
	with open(newfile, 'w+') as outfile:
		for line in edited_str_lines:
			outfile.write(line)


# adds edges to the building DAG
def build_dag(xml):
	building_dag = nx.DiGraph()
	parsed_xml = et.parse(xml)
	root = parsed_xml.getroot()
	for child in root.findall("child"):
		id = child.get('ref')
		for parent in child.findall("parent"):
			pid = parent.get('ref')
			building_dag.add_edge(pid, id)
	for node in building_dag.nodes:
		runtime = [e.get('runtime') for e in root.findall("job/[@id='{0}']".format(node))]
		building_dag.nodes[node]['comp'] = float(runtime[0])
		x = node

	for edge in building_dag.edges:
		output = [e.get('file') for e in root.findall("job/[@id='{0}']/uses/[@link='output'][@file]".format(edge[0]))]
		input = [e.get('file') for e in root.findall("job/[@id='{0}']/uses/[@link='input'][@file]".format(edge[1]))]
		sout = set(output)
		sinput = set(input)
		intersect_file = (sout & sinput)
		# CYBERSHAKE DOES SOMETHING DIFFERENT HERE (DON'T ASK ME WHY)
		if len(intersect_file) == 0:
			building_dag.edges[edge]['size'] = float(0)
		elif len(intersect_file) > 0:
			# Loop through each of the intersect files and add up the cumulative data
			total = 0
			for file in intersect_file:
				element = root.findall("job/[@id='{0}']/uses/[@link='output'][@file='{1}']".format(edge[0], file))
				total += float(element[0].get('size'))
			building_dag.edges[edge]['data_size'] = total
		else:
			sys.exit("Issues translating DAX")

	return building_dag


def generate_shadow_json(nxdag, path):
	"""
	Takes the provided networkx graph
	:param nxdag:
	:param path:
	:return:
	"""
	jgraph = {
		"header": {
			"time": False,
		},
		'graph': nx.readwrite.node_link_data(nxdag)
	}
	with open(path, "w") as wfile:
		json.dump(jgraph, wfile, indent=2)

if __name__ == '__main__':
	# reoves the unnecessary string (passed as parameter and outputs an edited file)
	clean_xml('test/data/shadowgen/Epigenomics_24.xml', 'test/data/shadowgen/edit_Epigenomics_24.xml', 'xmlns',
			'<adag version="2.1" count="1" index="0" name="test" jobCount="25" fileCount="0" childCount="20">\n')
	# moves edited xml to the nx DiGraph object
	finished_dag = build_dag('test/data/shadowgen/edit_Epigenomics_24.xml')

	# dumps the complete DAG from nx into json, now translated and ready for use
	generate_shadow_json(finished_dag,"test/data/shadowgen/translated_edit_Epigenomics_24.json")
