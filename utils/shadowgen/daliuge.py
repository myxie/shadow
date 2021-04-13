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
    cmd_list = ['dlg', 'unroll', '-fv', '-L',
                graph]
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
        node_identifier,
        seed=20,
        data_intensive=False):
    """
    Daliuge import will use
    :return: The NetworkX graph for visualisation purposed;
    The path of the output file; None if the process fails
    """
    random.seed(seed)
    # Process DALiuGE JSON graph
    unrolled_nx = _daliuge_to_nx(daliuge_json)

    translated_graph = _add_generated_values_to_graph(
        unrolled_nx, mean, uniform_range, ccr, multiplier, node_identifier,
        data_intensive
    )
    # Convering DALiuGE nodes to readable nodes

    jgraph = {
        "header": {
            "time": False,
            "gen_specs": {
                'file': daliuge_json,
                'mean': mean,
                'range': "+-{0}".format(uniform_range),
                'seed': seed,
                'ccr': ccr,
                'multiplier': multiplier
            },
        },
        'graph': nx.readwrite.node_link_data(translated_graph)
    }

    with open("{0}".format(output_file), 'w') as jfile:
        json.dump(jgraph, jfile, indent=2)

    return translated_graph, output_file


def _daliuge_to_nx(input_file):
    """
    Take a daliuge json file and read it into a NetworkX file
    :param input_file: the DALiuGE file we are translating
    :return: A NetworkX DiGraph.
    """
    if os.path.exists(input_file) and (os.stat(input_file).st_size != 0):

        with open(input_file) as f:
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

        edgedict = {}
        for val in graphdict:
            if 'producers' in val.keys():
                edgedict[val['oid']] = {'producers': [], 'consumers': []}
                edgedict[val['oid']]['producers'] = val['producers']
            if 'consumers' in val.keys():
                if val['oid'] in edgedict:
                    edgedict[val['oid']]['consumers'] = val['consumers']
                else:
                    edgedict[val['oid']] = {
                        'producers': [], 'consumers': val['consumers']
                    }

        for val in graphdict:
            if 'app' in val.keys():
                # There is a known bug in DALiuGE about this.
                if val['app'] == "dlg.apps.simple.SleepApp":
                    continue
            if 'outputs' in val:
                for output in val['outputs']:
                    for consumer in edgedict[output]['consumers']:
                        unrolled_nx.add_edge(val['oid'], consumer)
            if 'inputs' in val:
                for inputs in val['inputs']:
                    for producer in edgedict[inputs]['producers']:
                        unrolled_nx.add_edge(producer, val['oid'])

        for node in unrolled_nx.nodes():
            unrolled_nx.nodes[node]['label'] = unrolled_nx.nodes[node]['nm']

        return unrolled_nx


def _add_generated_values_to_graph(
        nxgraph,
        mean,
        uniform_range,
        ccr,
        multiplier,
        node_identifier,
        data_intensive=False
):
    """
    Produces a new graph that converts the DALiuGE Node labels into easier-to-read values,
    and adds the generated computation and data values to the nodes and edges respectively.
    :param nxgraph: The NetworkX DiGraph that is with raw DALiuGE node information
    :return: A NetworkX DiGraph
    """
    translation_dict = {}
    for i, node in enumerate(nx.topological_sort(nxgraph)):
        translation_dict[node] = i

    translated_graph = nx.DiGraph()
    for key in translation_dict:
        translated_graph.add_node(translation_dict[key])

    for edge in nxgraph.edges():
        (u, v) = edge
        translated_graph.add_edge(translation_dict[u], translation_dict[v])

    new = [node_identifier+str(node) for node in translated_graph.nodes()]
    mapping = dict(zip(translated_graph, new))
    translated_graph = nx.relabel_nodes(translated_graph,mapping)

    comp_dict = generator.generate_comp_costs(
        translated_graph.nodes, mean, uniform_range, multiplier
    )

    for node in translated_graph.nodes():
        # translated_graph.nodes[node]['label'] = node_identifier+str(node)
        translated_graph.nodes[node]['comp'] = comp_dict[node]

    # Generate data loads between edges and data-link transfer rates
    edge_dict = None
    if data_intensive:
        edge_dict = generator.generate_data_intensive_costs(
            translated_graph.edges, mean, uniform_range, multiplier, ccr
        )
    else:
        edge_dict = generator.generate_data_costs(
            translated_graph.edges, mean, uniform_range, multiplier, ccr
        )

    for edge in translated_graph.edges:
        translated_graph.edges[edge]['data_size'] = edge_dict[edge]

    return translated_graph
