# Copyright (C) 3/2/20 RW Bunney

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


"""
shadowgen is a utility that allows us to generate different testing scripts for shadow expeiriments

shadowgen will convert, translate, and generate workflow and environemnt files
"""
import subprocess
import os

CURR_DIR = "/home/rwb/Dropbox/PhD/writeups/observation_graph-model"
# TARGET_DIR = '/home/rwb/Dropbox/PhD/writeups/observation_graph-model/'
JSON_DIR = '/home/rwb/Dropbox/PhD/writeups/observation_graph-model/json/'

from sample_generator import generate_graph_costs , generate_system_machines

def dotgen(min,max,increment):
	print("Using Ggen graph generating library")

	'''
	Here, we loop through the range provided on the command line
	'''
	# prob = float(args[4])
	# increment = int(args[5])

	for x in range(min, max, increment):
		outfile = 'dots/ggen_out_{0}-denselu.dot'.format(x)
		print('Generating file: {0}'.format(outfile))
		subprocess.run(['ggen', '-o', '{0}'.format(outfile), 'dataflow-graph', 'denselu', str(x)])
	
def genjson():
	for path in sorted(os.listdir(CURR_DIR)):
		if 'dot' in path:
			print(os.listdir(CURR_DIR))
			print('Generating json for {0}'.format(path))
			generate_graph_costs('{0}/{1}'.format(CURR_DIR,path),
								 '/home/rwb/Dropbox/PhD/writeups/observation_graph-model/json/{0}.json'.format(
									 path[:-4]), 0.5, 5000, 500, 'giga')
			generate_system_machines(
				'/home/rwb/Dropbox/PhD/writeups/observation_graph-model/json/{0}_sys.json'.format(path[:-4]),
				512, 'giga', [0.9375, 0.0625], [(100, 150), (400, 500)])
