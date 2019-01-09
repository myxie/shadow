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

import unittest, random
from csv import reader

from experiments.graph_generator import random_wcost_matrix

class TestMatrixGenerator(unittest.TestCase):
    def setUp(self):
        random.seed(30)

    # Double check the seed is producing the right values
    def test_random_seed(self):
        random.seed(30)
        self.assertTrue(self.uniform_int(10,20) == 15)
        self.assertTrue(self.uniform_int(10,20) == 12)

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
        _min, _max = 10,20 
        seed = 30
        matrix = []
        random_wcost_matrix(_min,_max,processors,tasks,seed)
        matrix = self.read_matrix('{0}_wcost.csv'.format(tasks))
        print(matrix)
        self.assertTrue(matrix[0] == [15,12])
        self.assertFalse(matrix[2] == [12,14])

        

    def read_matrix(self,matrix):
        lmatrix = []
        f = open(matrix,'r',newline='')
        next(f)
        csv_reader = reader(f)
        for row in csv_reader:
            lmatrix.append(list(map(int,row)))
        f.close()
        return lmatrix 


    def uniform_int(self,min,max):
        return int(random.uniform(min, max))
