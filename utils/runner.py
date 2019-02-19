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

# Setup and run an experiment given a set of parameters

from classes.workflow import Workflow

from algorithms.heuristics import heft, pheft


def runner(graphname, ccost,wcost,algorithms=[]):
	"""
	Given the file name of the graph, and the wcost/ccost matrices, run the specified algorithms, 
	"""
	wf = Workflow(graphname,wcost,ccost)
	for alg in algorithms():
		if alg is 'heft':
			heft(wf)
		elif alg is 'pheft': 
			pheft(wf)

	return None

