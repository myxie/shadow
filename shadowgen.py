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
import logging

from utils.shadowgen.daliuge import unroll_graph, generate_dot_from_networkx_graph
from utils.shadowgen.ggen import genjson, dotgen

# from utils.shadowgen.dax import

logger = logging.getLogger(__name__)


def run_daliuge_translator(arg):
	print(arg)
	if arg['nc']:
		logger.info('Editing number of channels')
	pass


def ggen_generation(arg):
	print(arg)
	pass


def dax_translator(arg):
	print(arg)
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
	# This is what we get get when we do func(vars(args)...
	daliuge_parser.add_argument('lg', help='The logical graph that needs translating')
	daliuge_parser.add_argument('--nc', help='Edit the number of channels')
	daliuge_parser.add_argument('--log', help='Log-level for logger (default is warning)')
	daliuge_parser.set_defaults(func=run_daliuge_translator)

	ggen_parser = subparsers.add_parser('ggen', help=' Generate sample dataflow graphs using ggen')
	ggen_parser.set_defaults(func=ggen_generation)

	dax_parser = subparsers.add_parser('dax', help='Translate DAX files to shadow format')
	dax_parser.set_defaults(func=dax_translator)

	args = parser.parse_args()
	if not args.command:
		parser.print_help()
	if args.command == 'daliuge':
		args.func(vars(args))
	if args.command == 'ggen':
		args.func(vars(args))
	if args.command == 'dax':
		args.func(vars(args))
