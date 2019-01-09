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

# Functions to generate graphs and cost matrices for experiments

import random
import csv

def random_wcost_matrix(_min, _max, processors,tasks,seed):
	random.seed(seed)
	with open('{0}_wcost.csv'.format(tasks), 'w',newline='') as csvfile:
		writer = csv.writer(csvfile,delimiter=',')
		writer.writerow('P1,P2,...,Pn')
		for t in range(0,tasks):
			task_wcost = []
			for p in range(0,processors):
				# Create line of a matrix with uniformly distributed values
				task_wcost.append(int(random.uniform(_min,_max)))
			# Write line to csv file
			writer.writerow(task_wcost)


def random_ccost_matrix(min, max, processors, tasks):
	communication_matrix = [[0 for x in range(tasks)] for x in range(tasks)]
	communication_matrix = communication_matrix*2



def generate_cost_matrices(comp_cost_min,comp_cost_max,\
							comm_cost_min,comm_cost_max):
	
	"""
	Given a Communication/Computation cost ratio, produce a communication and computation cost matrix-pair of that ratio. 

	Values are picked from a uniform distribution from max/minimum values. 
	This means the mean value will be the mid point, which allows us to more easily represent ccr;

	IF we want a ccr of 0.1, then we can choose wcost range of 50-100, ccost range of 500-1000. This guaruntees a wcost average of 75 and 750 for wcost and ccost respectively, giving ccr of 0.1
	"""	

	return None
    # for val in os.listdir(location):
    #     graphs.append(location+val)

    # for path in graphs:
    #     print path
    #     graph = nx.read_graphml(path,Task)
    #     num_nodes= len(graph.nodes())

    #     if num_nodes > 5000:
    #         continue
    #     print path
    #     for x in range(3,9):
    #         random_comp_matrix(x,num_nodes,comp_cost_min,comp_cost_max)
    #         # random_comm_matrix(num_nodes,comm_cost_min,comm_cost_max) 
