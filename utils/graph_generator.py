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


# TODO Move from CSV to json format
def random_wcost_matrix(_min, _max, processors, tasks, seed, directory):
	csv_header = ['P1', 'P2', '...', 'Pn']
	random.seed(seed)
	with open('{0}/{1}_wcost_{2}-{3}.csv'.format(directory, tasks, _min, _max), 'w', newline='') as csvfile:

		writer = csv.writer(csvfile)
		writer.writerow(csv_header)
		writer = csv.writer(csvfile, delimiter=',')
		for t in range(0, tasks):
			task_wcost = []
			for p in range(0, processors):
				# Create line of a matrix with uniformly distributed values
				task_wcost.append(int(random.uniform(_min, _max)))
			# Write line to csv file
			writer.writerow(task_wcost)


def random_ccost_matrix(_min, _max, tasks, seed, directory):
	csv_header = ['T1', 'T2', '...', 'Tn']
	random.seed(seed)
	matrix = [[0 for x in range(tasks)] for x in range(tasks)]
	for x in range(tasks - 1):
		for y in range(x + 1, tasks):
			matrix[x][y] = int(random.uniform(_min, _max))
			matrix[y][x] = matrix[x][y]

		csvfile = open('{0}/{1}_ccost_{2}-{3}.csv'.format(directory, tasks, int(_min), int(_max)), 'w', newline='')
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(csv_header)
		for row in matrix:
			writer.writerow(row)


def generate_cost_matrices(seed, ccr, mean, uniform_range, processors, tasks, directory):
	"""
	Given a Communication/Computation cost ratio, produce a communication and computation cost matrix-pair of that ratio.

	Values are picked from a uniform distribution from max/minimum values.
	This means the mean value will be the mid point, which allows us to more easily represent ccr;

	IF we want a ccr of 0.1, then we can choose ccost range of 50-100, wcost range of 500-1000. This guaruntees
	a average of 75 and 750 for ccost and wcost respectively, giving ccr of 0.1
	# """
	# random.seed(seed)
	# comp_mean = random.randint(_min,_max)
	comp_min = mean - uniform_range
	comp_max = mean + uniform_range

	random_wcost_matrix(comp_min, comp_max, processors, tasks, seed, directory)

	comm_mean = int(mean * ccr)
	comm_min = comm_mean - (uniform_range * ccr)
	comm_max = comm_mean + (uniform_range * ccr)
	random_ccost_matrix(comm_min, comm_max, tasks, seed, directory)

	return comm_mean, comm_min


# TODO 
def cost_json_dump(array):
	# generate the node dictionary entry

	# generate the resource dictionary entry

	# Generate the edge dictionary
	edgedict = {}
	count = 0
	for node in mat:
		edgedict[count] = node
		count += 1

	# Dump to json
	import json
	fp = open('test.json', 'w')
	json.dump(newdict, fp, indent=4)
	fp.close()

	# edgedict={}
	# for tup in array:
	#     tuple2str = ','.join([str(x) for x in tup])
	#     edgedict[tuple2str] = 4*tup[1]
