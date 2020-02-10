# Copyright (C) 10/2/20 RW Bunney

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
import argparse
from utils.shadowgen.shadowgen import unroll_graph, dotgen,generate_dot_from_networkx_graph
def run_daliuge_translator():
	pass

def ggen_generation():
	pass

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='ScHeduling Algorithms for Data-Intensive			 Workflows')

	subparsers = parser.add_subparsers(help='Command', dest='command')

	# choices = list(cfg.test.keys())
	# test = { # Tests for the test runner
	# 	"workflow": test.test_workflow,
	# 	"graph_generator": test.test_graph_generator,
	# 	"heuristic": test.test_heuristic,
	# 	"metaheuristic": test.test_metaheuristic}

	daliuge_parser = subparsers.add_parser('daliuge', help='Unroll and Translate DALiuGE Logical Graph')
	daliuge_parser.add_argument('--all', action='store_true', help='Run all test')
	daliuge_parser.add_argument('--case', nargs='+', choices=list([]), help='Run the following test cases')

	daliuge_parser.set_defaults(func=run_daliuge_translator)

	ggen_parser = subparsers.add_parser('ggen', help=' Generate dataflow graphs using ggen')
	ggen_parser.set_defaults(func=ggen_generation)
	ggen_parser.add_argument('algorithm', help='Name of algorithm')
	ggen_parser.add_argument('workflow', help='Location of workflow config')
	ggen_parser.add_argument('environment', help='Location of the environment config')

	# TODO DAX parser
	dax_parser = subparsers.add_parser('dax', help='')


	args = parser.parse_args()
	if not args.command:
		parser.print_help()
	if args.command == 'algorithm':
		args.func(vars(args), ggen_parser)
	if args.command == 'test':
		args.func(vars(args),  daliuge_parser)
