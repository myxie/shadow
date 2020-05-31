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

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import RcParams
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)


class AllocationPlot(object):
	"""
	This is created when we want to generate an allocation plot for the results of a scheduled 
	workflow
	"""

	def __init__(self, solution):
		self.machines = solution.machines
		self.makespan = solution.makespan
		self.plotable_allocations = self._unwrap_allocation_tuples(solution)

		# We have a dictionary of the allocations, what do we do with them?
		pass

	def _unwrap_allocation_tuples(self,solution):
		alloc_list = []
		for i,m in enumerate(self.machines):
			alloc_list.append([])
			for alloc in solution.list_machine_allocations(m):
				alloc_list[i].append((alloc.ast, alloc.aft, alloc.tid))
		return alloc_list

	def plot(self, save=False, figname=None):
		num_machines = len(self.machines)
		fig, ax = plt.subplots(num_machines, sharex='row', sharey='col', gridspec_kw={'hspace': 0})
		self._setup_xaxis(num_machines, ax)
		data = self._format_data_for_imshow(self.plotable_allocations,num_machines,self.makespan,ax)
		self._use_imshow(data, ax, num_machines)
		self._setup_grid(num_machines,ax, self.machines)
		plt.xlabel('Makespan (s)')
		if save:
			plt.savefig(figname, dpi=300)
		else:
			plt.show()

	def _setup_grid(self, num_machines,ax,machines):
		for x,m in enumerate(machines):
			# Setup axis
			ax[x].grid(which='minor', axis='y', linestyle='-', color='w', linewidth=5)
			ax[x].set_yticks(np.arange(0, 0))
			ax[x].set_aspect('auto')
			ax[x].set(ylabel=m.id)

	def _setup_xaxis(self, num_machines, ax):
		ax[0].xaxis.set_major_locator(MultipleLocator(10))
		ax[0].xaxis.set_major_formatter(FormatStrFormatter('%d'))
		for x in range(0, num_machines):
			ax[x].set_yticks(np.arange(0, 2) - .5, minor=True)

	def _format_data_for_imshow(self, allocations,num_machines,makespan,ax):
		data = np.zeros((makespan+10, num_machines)).transpose()
		count = 0
		for machine in allocations:
			for tup in machine:
				# data[count][tup[0]]=0.5
				data[count][(tup[0]):(tup[1]) - 1] = 1
				# data[count][tup[1]]=0.5
				text = ax[count].text(
					(tup[1] + tup[0]) / 2,
					0,
					tup[2],
					horizontalalignment='center',
					verticalalignment='center',
					color="w"
				)
			# data[count][tup[1]+1]=0.5
			count += 1
		return data

	def _use_imshow(self, data, ax, num_machines):
		ax[0].imshow(np.array([data[0]]), cmap="Blues", origin='lower')
		for x in range(1, num_machines):
			ax[x].imshow(np.array([data[x]]), cmap="Blues")
		for a in ax:
			a.label_outer()


class BarPlot(object):
	def __init__(self):
		pass


