#!/usr/bin/env python 

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


# Configuration settings for this project

# Files and directorys for test data used in tests/
import tests.test_heuristic,tests.test_graph_generator, tests.test_workflow,\
		tests.test_metaheuristic

tests = { 'workflow': tests.test_workflow,
        'graph_generator': tests.test_graph_generator,
        'heuristic': tests.test_heuristic,
        'metaheuristic': tests.test_metaheuristic}


test_dir = 'tests/data'

test_heuristic_data = {	# Tests that use the Topcuoglu paper graph
						'topcuoglu_graph': 'tests/data/topcuoglu.graphml',
						'heft_attr': 'tests/data/heft_attr.json',
						'flops_test_attr':'tests/data/flop_rep_test.json',

						# Tests that use the PHEFT paper graph
						'pheft_graph': 'tests/data/pheft.graphml',
						'pheft_attr': 'tests/data/pheft_attr.json',
						# 'pheft_ccost':'tests/data/oct_comm.txt',
					}

test_generator_data = {	'wcost_matrix': 'tests/data/5_wcost_10-20.csv',
						'ccost_matrix': 'tests/data/5_ccost_10-20.csv',

						'ccr_check_wcost': 'tests/data/5_wcost_100-200.csv',
						'ccr_0.1_ccost': 'tests/data/5_ccost_10-20.csv',
						'ccr_10_ccost': 'tests/data/5_ccost_1000-2000.csv'}