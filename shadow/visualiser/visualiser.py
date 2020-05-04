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
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

# figure(num=None,figsize=(10,100))

makespan = 98
x_axis_max_len = 105

p1 = [(29, 42, '1'), (60, 81, '7'), (84, 98, '9')]
p2 = [(22, 40, '4')]
p3 = [(0, 11, '0'), (11, 21, '3'), (21, 30, '2'), (30, 45, '5'), (45, 55, '6'), (58, 71, '8')]
fig, ax = plt.subplots(3, sharex='row', sharey='col', gridspec_kw={'hspace': 0})
procs = [p1, p2, p3]
data = np.zeros((105, 3)).transpose()
count = 0
# print(data[count])
for proc in procs:
	for tup in proc:
		# data[count][tup[0]]=0.5
		data[count][(tup[0]):(tup[1])-1] = 1
		# data[count][tup[1]]=0.5
		text = ax[count].text((tup[1] + tup[0]) / 2, 0, tup[2], horizontalalignment='center',
							  verticalalignment='center', color="w")
	# data[count][tup[1]+1]=0.5
	count += 1
print(data)

# Set figure width to 12 and height to 9
# fig_size=(8,6)
# # fig_size[0] = 12
# # fig_size[1] = 9
# plt.rcParams["figure.figsize"] = fig_size
# create discrete colormap
# cmap = colors.ListedColormap(['red', 'blue'])
# bounds = [0,100,100]
# norm = colors.BoundaryNorm(bounds, cmap.N)
ax[0].xaxis.set_major_locator(MultipleLocator(10))
ax[0].xaxis.set_major_formatter(FormatStrFormatter('%d'))


ax[0].imshow(np.array([data[0]]), cmap="Blues",origin='lower')
ax[1].imshow(np.array([data[1]]), cmap="Blues")
ax[2].imshow(np.array([data[2]]), cmap="Blues")
for a in ax:
	a.label_outer()
# fig.dpi=1000
# draw gridlines
ax[0].set_yticks(np.arange(0, 2) - .5, minor=True)
ax[1].set_yticks(np.arange(0, 2) - .5, minor=True)
ax[2].set_yticks(np.arange(0, 2) - .5, minor=True)
# ax[0].set_xticks(xticks)
ax[0].grid(which='minor', axis='y', linestyle='-', color='w', linewidth=5)
# ax.grid(which='major', axis='x', linestyle='-', color='w', linewidth=1)
ax[0].set_yticks(np.arange(0, 0))
ax[0].set_aspect('auto')
ax[0].set(ylabel='machine0')

ax[1].grid(which='minor', axis='y', linestyle='-', color='w', linewidth=5)
# ax.grid(which='major', axis='x', linestyle='-', color='w', linewidth=1)
ax[1].set_yticks(np.arange(0, 0))
ax[1].set_aspect('auto')
ax[0].set(ylabel='machine1')

ax[2].grid(which='minor', axis='y', linestyle='-', color='w', linewidth=5)
# ax.grid(which='major', axis='x', linestyle='-', color='w', linewidth=1)
ax[2].set_yticks(np.arange(0, 0))
ax[2].set_aspect('auto')
ax[0].set(ylabel='machine2')

plt.show()


class AllocationPlot(object):
	"""
	This is created when we want to generate an allocation plot for the results of a scheduled 
	workflow
	"""
	def __init__(self, workflow):
		pass
	

class BarPlot(object):
	def __init__(self):
		pass