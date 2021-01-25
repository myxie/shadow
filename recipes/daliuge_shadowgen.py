# Copyright (C) 28/7/20 RW Bunney

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

# Example Recipe for generating graph costs and homogeneous cluster on which to
# run a (BASIC) DALiuGE Graph, generated from the EAGLE template
import logging
import json

import networkx as nx

from utils.shadowgen import daliuge
from utils.shadowgen import generator

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

# System Reqs.
HETEROGENEITY = [0.75,0.25]  # Homogeneous
NUM_MACHINES = 40
SPEC_RANGE = [(200,400),(800,1600)]
MAGNITUDE = 'giga'
SYSTEM_OUTPUT_PATH = 'recipes/routput/system_spec_{0}_{1}_{2}'.format(
    NUM_MACHINES,
    "{0}-{1}".format(SPEC_RANGE[0 ][0],SPEC_RANGE[1][1]),
    "{0}-{1}".format(HETEROGENEITY[0], HETEROGENEITY[1])
)

# Graph Reqs.
LOGICAL_GRAPH = 'recipes/rdata/SDPContinuumPipeline_UpdatedNoOuter.graph'
# DALIUGE_GRAPH = 'TestAskapCont.graph'
SHADOW_OUTPUT = 'recipes/routput/shadow_TestAskapCont.json'
MEAN = 500000  # Mean of 5000/range of 500 gives us a distribution between
# 4500-5500
UNIFORM_RANGE = 400000
MULTIPLIER = 1
CCR = 0.001  # CCR < 1 -> Data time > Comp time
logger.debug('Heterogeneity length: {0}'.format(len(HETEROGENEITY)))
# Generating the syste
system_config_path = generator.generate_system_machines(
    SYSTEM_OUTPUT_PATH, NUM_MACHINES, MAGNITUDE, HETEROGENEITY, SPEC_RANGE
)
logger.info(system_config_path)

# Generating graph costs
unrolled_graph_json = daliuge.unroll_logical_graph(LOGICAL_GRAPH)

graph_list = []

CHANNELS = 2
for i in range(0, CHANNELS):
    identifier = "c{0}_".format(i)
    nxgraph,output_graph_path = daliuge.json_to_shadow(
        unrolled_graph_json, SHADOW_OUTPUT, MEAN, UNIFORM_RANGE, MULTIPLIER,
        CCR,node_identifier=identifier,
        seed=20, data_intensive=True
    )
    graph_list.append(nxgraph)

head = 'channel_split'
channel_graph = nx.DiGraph()
children = [head+str(i) for i in range(0,CHANNELS)]
channel_graph.add_nodes_from(children)
channel_graph.add_node(head)
channel_graph.add_edges_from([(head, head+str(x)) for x in range(0, CHANNELS)])
for node in channel_graph.nodes():
    channel_graph.nodes[node]['comp'] = 100000
for edge in channel_graph.edges():
    channel_graph.edges[edge]['data_size']=0
i = 0
# glist = []
# for x in range(0,len(children)):
#     ng = nx.DiGraph()
#     ng.add_nodes_from([z for z in range(i, i + len(children))])
#     ng.add_edges_from([(z, z + 1) for z in range(i, i+len(children)-1)])
#     glist.append(ng)
#     i += len(children)

glistgraph = nx.compose_all(graph_list)
final = nx.compose(glistgraph, channel_graph)

for i in range(0,CHANNELS):
    minor_heads = []
    for node in graph_list[i].nodes():
        pred = list(final.predecessors(node))
        if len(pred) == 0:
            minor_heads.append(node)
    for node in minor_heads:
        final.add_edge(head+str(i),node,data_size=0)

nx.drawing.nx_pydot.write_dot(final, 'testgraph.dot')

jgraph = {
    "header": {
        "time": False,
        "gen_specs": {
            'file': "channel_split_continuum.json",
            'mean': MEAN,
            'range': "+-{0}".format(UNIFORM_RANGE),
            'seed': 20,
            'ccr': CCR,
            'multiplier': MULTIPLIER
        },
    },
    'graph': nx.readwrite.node_link_data(final)
}

with open(
        "{0}".format(
            "recipes/routput/shadow_Continuum_ChannelSplit.json"
        ),'w'
) as jfile:
    json.dump(jgraph, jfile, indent=2)


daliuge.generate_dot_from_networkx_graph(final,'output')

logger.info(output_graph_path)

