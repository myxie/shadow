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

from utils.shadowgen import daliuge
from utils.shadowgen import generator

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

# System Reqs.
HETEROGENEITY = [1.0]  # Homogeneous
NUM_MACHINES = 20
SPEC_RANGE = [(200,400)]
MAGNITUDE = 'giga'
SYSTEM_OUTPUT_PATH = 'recipes/routput/system_spec_{0}_{1}_{2}'.format(
	NUM_MACHINES,
	SPEC_RANGE,
	HETEROGENEITY
)

# Graph Reqs.
LOGICAL_GRAPH = 'recipes/rdata/SDPContinuumPipeline_UpdatedNoOuter.graph'
# DALIUGE_GRAPH = 'TestAskapCont.graph'
SHADOW_OUTPUT = 'recipes/routput/shadow_TestAskapCont.json'
MEAN = 5000  # Mean of 5000/range of 500 gives us a distribution between 4500-5500
UNIFORM_RANGE = 1000
MULTIPLIER = 1
CCR = 0.5  # CCR < 1 -> Data time > Comp time
logger.debug('Heterogeneity length: {0}'.format(len(HETEROGENEITY)))
# Generating the syste
system_config_path = generator.generate_system_machines(
	SYSTEM_OUTPUT_PATH, NUM_MACHINES, MAGNITUDE, HETEROGENEITY, SPEC_RANGE
)
logger.info(system_config_path)

# Generating graph costs
unrolled_graph_json = daliuge.unroll_logical_graph(LOGICAL_GRAPH)
nxgraph,output_graph_path = daliuge.json_to_shadow(unrolled_graph_json, SHADOW_OUTPUT, MEAN, UNIFORM_RANGE, MULTIPLIER, CCR)
daliuge.generate_dot_from_networkx_graph(nxgraph,'output')
logger.info(output_graph_path)

