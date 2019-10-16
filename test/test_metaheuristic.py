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


import unittest

import config as cfg
from shadow.algorithms.metaheuristic import generate_population,\
                                     generate_allocations,\
                                     non_dom_sort



from shadow.classes.workflow import Workflow

class TestPopulationGeneration(unittest.TestCase):
    """
    Tests how we generate solutions for NSGAII and SPEAII
    """ 

    def setUp(self):
        self.wf = Workflow(cfg.test_heuristic_data['topcuoglu_graph'])
        self.wf.load_attributes(cfg.test_heuristic_data['heft_attr'],calc_time=False)

    def test_pop_gen(self):
        seed = 10
        a= generate_population(self.wf,10,seed,2)
        # for x in a: 
        #     print(x.exec_order)
        b= generate_population(self.wf,10,seed,2)

        self.assertTrue(a==a)
        seed = 47

        b= generate_population(self.wf,10,seed,2)
        self.assertFalse(a==b)

        # for soln in a: 
        #     print(soln.task_assign)

    def test_allocation(self):
        seed = 10
        a = generate_allocations(self.wf.graph.number_of_nodes(),10, 4,seed)
        # print(a)  
        # a = generate_allocations(self.wf.graph.number_of_nodes(),10, 4,seed)
        # print(a)

    def test_nondomsort(self):
        seed = 10
        pop = generate_population(self.wf,10,seed,2)
        objectives = []
        # print(pop)
        non_dom_sort(pop,objectives)
        for p in pop: 
            print(p.nondom_rank)
