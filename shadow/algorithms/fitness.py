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

"""
Fitness functions for use in evaluating objectives
"""

FIT_COST = 'cost'
FIT_TIME = 'time'
FIT_THROUGPUT = 'throughput'
FIT_REL = 'reliability'

def cost_fitness(solution):
	"""
	Calculate the cost of the solution based on the environment
	:param solution:
	:return: cost
	"""

	cost = 0

	for machine in solution.machines:
		tmpcost = 0
		cost = machine.cost
		for allocation in solution.list_machine_allocations(machine):
			runtime = allocation.aft-allocation.ast
			tmpcost += runtime*cost
		cost+=tmpcost
	return cost


def time_fitness(solution):
	"""
	Return the runtime of the solution based on the environment
	:param solution:
	:return:
	"""
	return solution.makespan


def throughput_fitness():
	return None


def reliability_fitness():
	return None



# This is ugly - I should place this somewhere else (e.g current_globs.py)
# which keeps the current state of the shadow library options available; e.g.
# visualisation parameters, objectives that can be tested etc.

objective_set = {"cost": cost_fitness,
				"time": time_fitness,
				"throughput": throughput_fitness,
				"reliability": reliability_fitness}


def run_objectives(objectives):
	retdict = {}
	for objective in objectives:
		if objective in objective_set:
			func = objective_set[objective]
			retdict[objective] = func()

	return None
