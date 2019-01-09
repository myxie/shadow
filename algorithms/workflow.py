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
# Copyright (C) [Date] RW Bunney


"""
Workflow class acts as a wrapper for all things associated with a task
workflow. A workflow object is a struct to keep associated data
together. 
"""

from csv import reader

import networkx as nx


class Workflow(object):


    def __init__(self, wcost, ccost, graphml):
        """
        :params wcost - work cost matrix
        :paramts ccost - communication cost matrix
        :graphml - graphml file in which workflows are stored
        """
        
        self.graph = nx.read_graphml(graphml,int)

        #This is all accessible from self.graph, bur for clearer code we make
        #it directly available from the workflow object
    
        self.wcost = self._read_matrix(wcost)
        self.ccost = self._read_matrix(ccost)

        num_processors  =len(self.wcost[0])
        self.processors = [[] for x in range(0,num_processors)]

        


    def _read_matrix(self,matrix):
        lmatrix = []
        f = open(matrix)
        next(f)
        csv_reader = reader(f)
        for row in csv_reader:
            lmatrix.append(list(map(int,row)))
        f.close()
        return lmatrix 
