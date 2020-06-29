# Copyright (C) 6/20 RW Bunney

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

from queue import Queue
from shadow.models.workflow import Workflow, Task


def sequential_execution(workflow):
	seq_eq = -1
	for machine in workflow.env.machines:
		tmp = 0
		for task in workflow.tasks:
			tmp += task.calculated_runtime[machine]
		if seq_eq < 0 or seq_eq < tmp:
			seq_eq = tmp
	return seq_eq


# TODO Update this to ensure it corresponds with Topcuoglu et al.'s defintion of CPmin
def critical_path_min(workflow):
	"""
	Critical path using the minimum cost (for SLR calculation)
	Use the minimum cost per task to calculate the CP

	:param workflow:
	:return:
	"""
	top_sort = workflow.sort_tasks("topological")
	dist = [-1 for x in range(len(list(workflow.graph.nodes())))]
	dist[0] = 0
	critical_path = []

	for u in top_sort:
		for v in list(workflow.graph.edges(u)):
			if dist[v[1].tid] < dist[u.tid] + min(workflow.tasks[v].calculated_runtime.values()):
				dist[v[1].tid] = dist[u.tid] + min(workflow.tasks[v].calculated_runtime.values())

	final_dist = dist[len(list(workflow.tasks)) -1]
	critical_path.append(len(list(list(graph.nodes()))) - 1)
	q = Queue()
	q.put(len(list(self.graph.nodes())) - 1)

	while not q.empty():
		u = q.get()
		tmp_max = 0
		for v in list(workflow.graph.predecessors(Task(u))):
			if dist[v.tid] > tmp_max:
				tmp_max = dist[v.tid
				tmp_v = v.tid
				if tmp_v not in critical_path:
					critical_path.append(tmp_v)
				q.put(tmp_v)
			elif dist[v.tid] is 0:
				tmp_v = 0  # this is the first node in the graph
				if tmp_v not in critical_path:
					critical_path.append(tmp_v)
	cp_min = 0
	for x in critical_path:
		cp_min = cp_min + min(self.comp_matrix[x])

	return cp_min