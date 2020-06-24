# Copyright (C) 19/6/20 RW Bunney

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

# Here we demonstrate allocations of different algorithms

import shadow.models.workflow as swf
import shadow.models.environment as senv
import shadow.algorithms.heuristic as sheuristic
import shadow.visualiser.plot as splot
import matplotlib.pyplot as plt

#
# heft_workflow = swf.Workflow('final_heft.json')
# fcfs_workflow = swf.Workflow('final_heft.json')
# shared_env = senv.Environment('final_heft_sys.json')
#
# heft_workflow.add_environment(shared_env)
# fcfs_workflow.add_environment(shared_env)
#
# heft_solution = sheuristic.heft(heft_workflow)
# fcfs_solution = sheuristic.fcfs(fcfs_workflow)
#
# max_x = max(heft_solution.makespan,fcfs_solution.makespan)
#
# heft_plot = splot.AllocationPlot(heft_solution)
# heft_fig, heft_ax = heft_plot.plot()
# for x in heft_ax:
# 	x.set_xlim(right=max_x+10)
# # heft_ax.set_xlim(right=1000)
# # plt.xlim([0,max_x+10])
# plt.show()
# fcfs_plot = splot.AllocationPlot(fcfs_solution)
# fcfs_fig, fcfs_ax = fcfs_plot.plot()
# for x in fcfs_ax:
# 	x.set_xlim(right=max_x+10)
# # plt.xlim([0,max_x+10])
# plt.show()


heft_workflow = swf.Workflow('../dax_files/output/shadow_Epigenomics_24.json')
fcfs_workflow = swf.Workflow('../dax_files/output/shadow_Epigenomics_24.json')
shared_env = senv.Environment('../environments/sys.json')

heft_workflow.add_environment(shared_env)
fcfs_workflow.add_environment(shared_env)

heft_solution = sheuristic.heft(heft_workflow)
fcfs_solution = sheuristic.fcfs(fcfs_workflow)
# max_x = max(heft_solution.makespan,fcfs_solution.makespan)

print(heft_solution.makespan)

heft_plot = splot.AllocationPlot(heft_solution)
heft_fig, heft_ax = heft_plot.plot()
# for x in heft_ax:
# 	x.set_xlim(right=max_x+10)
# heft_ax.set_xlim(right=1000)
# plt.xlim([0,max_x+10])
plt.show()
fcfs_plot = splot.AllocationPlot(fcfs_solution)
fcfs_fig, fcfs_ax = fcfs_plot.plot()
# # for x in fcfs_ax:
# # 	x.set_xlim(right=max_x+10)
# # plt.xlim([0,max_x+10])
plt.show()

