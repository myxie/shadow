# Copyright (C) 6/2/20 RW Bunney

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

metric_map = ['slr, speedup, efficiency']

""" 
These metrics are derived from Kwok and Ahmed 1998  
"""


def schedule_to_length(solution):
	pass


def speedup(workflow):
	sequential_execution = -1
	for machine in workflow.env.machines:
		tmp = 0
		for task in workflow.tasks:
			tmp += task.calculated_runtime[machine]
		if sequential_execution < 0 or sequential_execution < tmp:
			sequential_execution = tmp

	speedup = workflow.solution.makespan/sequential_execution

	return speedup


def efficiency():
	pass
