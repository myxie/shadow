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

import test as project_tests
from algorithms.heuristic import heft
from classes.workflow import Workflow

testcases = {  # Tests for the test runner
	"workflow": project_tests.test_workflow,
	"graph_generator": project_tests.test_graph_generator,
	"heuristic": project_tests.test_heuristic,
	"metaheuristic": project_tests.test_metaheuristic
}


def run_tests(args, tests, curr_parser):
	if args['all']:
		suite = unittest.TestSuite()
		loader = unittest.TestLoader()
		for test in tests:
			suite.addTests(loader.loadTestsFromModule(tests[test]))
		runner = unittest.TextTestRunner()
		runner.run(suite)
		return True

	if args['case']:
		for case in args['case']:
			suite = unittest.TestSuite()
			loader = unittest.TestLoader()
			suite.addTests(loader.loadTestsFromModule(tests[case]))
			runner = unittest.TextTestRunner()
			runner.run(suite)
	else:
		curr_parser.print_help()


def run_algorithm(args, parser):
	if args['algorithm'] == 'heft':
		wf = Workflow(args['graph'])
		calc_time = (args['calc_time'] == 'True')
		wf.load_attributes(args['attr'], calc_time)
		heft(wf)
		wf.pretty_print_allocation()


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Multi-Objective Workflow Scheduling Modelling Suite')

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
