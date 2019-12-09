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

# Files and directorys for test data used in test/


# test_dir = 'test/data'

test_heuristic_data = {  # Tests that use the Topcuoglu paper graph
	'topcuoglu_graph': 'test/data/final_heft.json',
	'topcuoglu_graph_nocalc': 'test/data/heuristic/heft_nocalc.json',
	'flops_test_attr': 'test/data/flop_rep_test.json',
	"topcuoglu_graph_system": 'test/data/heuristic/final_heft_sys.json',
	# Tests that use the PHEFT paper graph
	'pheft_graph': 'test/data/heuristic/pheft_nocalc.json',
	# 'pheft_attr': 'test/data/pheft_attr.json',
	# 'pheft_ccost':'test/data/oct_comm.txt',
}
test_workflow_data = {  # Tests that use the Topcuoglu paper graph
	'topcuoglu_graph': 'test/data/workflow/final_heft.json',
	'topcuoglu_graph_nocalc': 'test/data/workflow/heft_nocalc.json',
	'flops_test_attr': 'test/data/flop_rep_test.json',
	"topcuoglu_graph_system": 'test/data/workflow/final_heft_sys.json',
	# Tests that use the PHEFT paper graph
	'pheft_graph': 'test/data/pheft_nocalc.json',
	# 'pheft_attr': 'test/data/pheft_attr.json',
	# 'pheft_ccost':'test/data/oct_comm.txt',
}

test_generator_data = {
	'wcost_matrix': 'test/data/5_wcost_10-20.csv',
	'ccost_matrix': 'test/data/5_ccost_10-20.csv',
	'ccr_check_wcost': 'test/data/5_wcost_100-200.csv',
	'ccr_0.1_ccost': 'test/data/5_ccost_10-20.csv',
	'ccr_10_ccost': 'test/data/5_ccost_1000-2000.csv'
}

test_environment_data = {
	'environment_sys': 'test/data/environment/ggen_out_2-denselu_sys.json'
}

