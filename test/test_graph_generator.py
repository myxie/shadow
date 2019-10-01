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

# Test cases for graph and matrix generation

import unittest
import random
import os
from csv import reader

from utils.graph_generator import random_wcost_matrix, \
	random_ccost_matrix, \
	generate_cost_matrices

import config as cfg


class TestMatrixGenerator(unittest.TestCase):
	def setUp(self):
		random.seed(30)

	def tearDown(self):
		for key in cfg.test_generator_data:
			if os.path.isfile(cfg.test_generator_data[key]):
				os.remove(cfg.test_generator_data[key])

	# Double check the seed is producing the right values
	def test_random_seed(self):
		random.seed(30)
		self.assertTrue(self.uniform_int(10, 20) == 15)
		self.assertTrue(self.uniform_int(10, 20) == 12)

		# Test global generation with another seeed value
		# random.seed(10000)
		# tasks = 100
		# machines = 2
		# #_min, _max = 10,20
		# seed = 10000
		# ccr= 10
		# mean = 1250
		# uniform_range =  500

		# generate_cost_matrices(seed,ccr, mean, uniform_range,machines,
		#                                             tasks,cfg.test_dir)

	def test_wcost_matrixGenerator(self):
		"""
		Produce a 5 x 2 matrix
		# Row 1: [15,12]
		# Row 2: [10,16]
		# Row 3: [12,12]
		# Row 4: [13,16]
		# Row 5: [19,14]
		"""
		tasks = 5
		processors = 2
		_min, _max = 10, 20
		seed = 30
		matrix = []
		random_wcost_matrix(_min, _max, processors, tasks, seed, cfg.test_dir)
		matrix = self.read_matrix(cfg.test_generator_data['wcost_matrix'])
		self.assertTrue(matrix[0] == [15, 12])
		self.assertFalse(matrix[2] == [12, 14])

	def test_ccost_matrixGenerator(self):
		"""
		Produce a 5 x 5 matrix
		# Row 1: [15,12,10,16,12]
		# Row 2: [15,0,12,12,13] 16 //19,14]
		"""
		tasks = 5
		_min, _max = 10, 20
		seed = 30
		matrix = []
		random_ccost_matrix(_min, _max, tasks, seed, cfg.test_dir)
		matrix = self.read_matrix(cfg.test_generator_data['ccost_matrix'])
		self.assertTrue(matrix[0] == [0, 15, 12, 10, 16])

	def testMatrixGenerator(self):
		"""
		For seed value 30, min/max values of 100/200, the following comp matrix should be produced:
		Row1    153,128
		Row2    103,165
		Row3    121,125
		Row4    139,164
		Row5    198,146

		The comm-cost matrix should return the same matrix in test_ccost_matrixGenerator()
		"""
		tasks = 5
		processors = 2
		# min, _max = 10,20
		seed = 30
		ccr = 0.1
		mean = 150
		uniform_range = 50

		comm_mean, comm_min = generate_cost_matrices(seed, ccr, mean,
													 uniform_range, processors, tasks, cfg.test_dir)
		comp_matrix = self.read_matrix(
			cfg.test_generator_data['ccr_check_wcost'])

		comm_matrix = self.read_matrix(
			cfg.test_generator_data['ccr_0.1_ccost'])
		self.assertTrue(comm_mean == 15)
		self.assertTrue(comp_matrix[3] == [139, 164])
		self.assertTrue(comm_matrix[0] == [0, 15, 12, 10, 16])

		ccr = 10
		comm_mean, comm_min = generate_cost_matrices(seed, ccr, mean,
													 uniform_range, processors, tasks, cfg.test_dir)
		comp_matrix = self.read_matrix(
			cfg.test_generator_data['ccr_check_wcost'])

		comm_matrix = self.read_matrix(
			cfg.test_generator_data['ccr_10_ccost'])
		self.assertTrue(comm_mean == 1500)
		self.assertTrue(comm_min == 1000)

		self.assertTrue(comm_matrix[1][2] >= 1200)

	def read_matrix(self, matrix):
		lmatrix = []
		f = open(matrix, 'r', newline='')
		next(f)
		csv_reader = reader(f)
		for row in csv_reader:
			lmatrix.append(list(map(int, row)))
		f.close()
		return lmatrix

	def uniform_int(self, min, max):
		return int(random.uniform(min, max))
