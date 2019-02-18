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


"""
Workflow class acts as a wrapper for all things associated with a task
workflow. A workflow object is a struct to keep associated data
together. 
"""

import json
from csv import reader

import networkx as nx
import numpy as np

class Workflow(object):

    def __init__(self,graphml):
        """
        :params wcost - work cost matrix
        :paramts ccost - communication cost matrix
        :graphml - graphml file in which workflows are stored
        """
        
        self.graph = nx.read_graphml(graphml,int)


    def load_attributes(self,attr,calc_time=True,perc_peak=1.0):
        """
        Attributes in the json file: 
        'comp' - the total FLOPS cost of each task 
        'resource' - the supplied FLOP/s 
        'edge' - a second dictionary in which the data products between nodes is stored

        If calc_time is True, then we calculate how much time each tasks takes based on the resource demand of the application and the supplied FLOPs/sec provided by each 'resource'

        If calc_time is False, then the time has already been calculated, and we have been provided with a cost vector per task instead. 

        """

        fp_attr = open(attr,'r')
        attr_dict = json.load(fp_attr)
        fp_attr.close()

        wcost,resource_vec = [],[]
        data_size={}
        if 'comp' in attr_dict: 
            wcost = attr_dict['comp']
        else: 
            return -1 # Attribute is not in json file

        if 'resource' in attr_dict: 
            resource_vec = attr_dict['resource']
        else: 
            return -1 

        if 'edge' in attr_dict: 
            data_size = attr_dict['edge']
        else: 
            return -1 

        if calc_time:
            for node in self.graph.node:
                self.graph.node[node]['comp'] = np.round(np.divide(wcost[node],resource_vec)).astype(int)                
        else:
            for node in self.graph.node:
                self.graph.node[node]['comp']=wcost[node]

        # TODO implement second data approach, which takes the rate of transfer between resources and calculates time based on that. 
        for edge in self.graph.edges:
            pred,succ = edge[0],edge[1]
            self.graph.edges[pred,succ]['data_size']=data_size[str(pred)][succ]
        
        self.processors = [[] for x in range(len(resource_vec))] 
        self.makespan = 0

        return 0


    def pretty_print_allocation(self):

        for p in self.processors:
            p = sorted(p)
            # print(p)
        print() 


        for x in range(len(list(self.graph.nodes))):
            print(x,end='\t')
            tabstop=""
            for p in range(len(self.processors)):
                if x < len(self.processors[p]):
                    print("{0}".format(self.processors[p][x]),end='\t')
                else:
                    tabstop = '\t\t'
                    print(tabstop,end='')
            print()

        print("Total Makespan: {0}".format(self.makespan))


        # wcost_vec = attr_dict['cost']
        # resource_vec = attr_dict['resource']
        # data_size = attr_dict['edges']

        # wcost_vec = self._read_matrix(wcost_vec)
        # resource_vec = self._read_matrix(resource_vec)
        # # ccost = self._read_matrix(ccost)

        # data_rates = self._read_matrix(rates)
        # data_size = self._read_matrix(sizes)

        # for node in self.graph.node:
        #     self.graph.node['comp'] = np.round(np.divide(wcost_vec[node],resource_vec)).astype(int)



        


    def _read_matrix(self,matrix):
        lmatrix = []
        f = open(matrix)
        next(f)
        csv_reader = reader(f)
        for row in csv_reader:
            lmatrix.append(list(map(int,row)))
        f.close()
        return lmatrix 
