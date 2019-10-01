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

# Mosws.py is the entry point for running test and experiments from the command line


import argparse, unittest

import test.test_workflow, test.test_heuristic 
from algorithms.heuristic import heft
from classes.workflow import Workflow

testcases = {  # Tests for the test runner
	"workflow": test.test_workflow,
	"heuristic": test.test_heuristic
}


def run_tests(arg, tests, curr_parser):
	if arg['all']:
		suite = unittest.TestSuite()
		loader = unittest.TestLoader()
		for test in tests:
			suite.addTests(loader.loadTestsFromModule(tests[test]))
		runner = unittest.TextTestRunner()
		runner.run(suite)
		return True

	if arg['case']:
		for case in arg['case']:
			suite = unittest.TestSuite()
			loader = unittest.TestLoader()
			suite.addTests(loader.loadTestsFromModule(tests[case]))
			runner = unittest.TextTestRunner()
			runner.run(suite)
	else:
		curr_parser.print_help()

def run_shadow():
	"""
	env = Environment(environment_config)
	wf = Workflow(workflow_config)
	wf.add_environment()
	env.run_workflows(heuristic.heft)

	:return:
	"""
	pass

def run_algorithm(arg, parser):
	if arg['algorithm'] == 'heft':
		wf = Workflow(arg['graph'])
		calc_time = (arg['calc_time'] == 'True')
		wf.load_attributes(arg['attr'], calc_time)
		heft(wf)
		wf.pretty_print_allocation()


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='ScHeduling Algorithms for Data-Intensive			 Workflows')

	subparsers = parser.add_subparsers(help='Command', dest='command')

	# choices = list(cfg.test.keys())
	# test = { # Tests for the test runner
	# 	"workflow": test.test_workflow,
	# 	"graph_generator": test.test_graph_generator,
	# 	"heuristic": test.test_heuristic,
	# 	"metaheuristic": test.test_metaheuristic}

	test_parser = subparsers.add_parser('test', help='Test Runner')
	test_parser.add_argument('--all', action='store_true', help='Run all test')
	test_parser.add_argument('--case', nargs='+', choices=list(testcases), help='Run the following test cases')

	test_parser.set_defaults(func=run_tests)

	algorithm_parser = subparsers.add_parser('algorithm', help='Run a single algorithm on a given data file')
	algorithm_parser.set_defaults(func=run_algorithm)
	algorithm_parser.add_argument('algorithm', help='Name of algorithm')
	algorithm_parser.add_argument('graph', help='Location of graphml file')
	algorithm_parser.add_argument('attr', help='Location of attributes file')
	algorithm_parser.add_argument('--calc_time', help='Set calc_time True/False', choices=['True', 'False'])

	args = parser.parse_args()
	if not args.command:
		parser.print_help()
	if args.command == 'algorithm':
		args.func(vars(args), algorithm_parser)
	if args.command == 'test':
		args.func(vars(args), testcases, test_parser)
