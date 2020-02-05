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
EAGLE_GRAPH = 'daliuge_graphs/TestAskapCont.graph'
CHANNELS = 10 

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
