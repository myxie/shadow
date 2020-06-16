from queue import Queue


def sequential_execution(self):
	# TODO Add test case for this
	seq = -1

	for p in range(len(self.processors)):
		comp = 0
		for task in list(self.graph.nodes()):
			comp = comp + self.comp_matrix[task.tid][p]
		if (seq is -1) or (comp < seq):
			seq = comp

	return seq


# TODO Update this to ensure it corresponds with Topcuoglu et al.'s defintion of CPmin
def critical_path_min(self):
	"""
	Critical path using the minimum cost (for SLR calculation)
	Use the minimum cost per task to calculate the CP
	:param self:
	:return:
	"""
	top_sort = self.top_sort_tasks()
	dist = [-1 for x in range(len(list(self.graph.nodes())))]
	dist[0] = 0
	critical_path = []

	for u in top_sort:
		for v in list(self.graph.edges(u)):
			tmp_v = v[1]
			if dist[v[1].tid] < dist[u.tid] + min(self.comp_matrix[v[1].tid]) + self.comm_matrix[v[1].tid][u.tid]:
				dist[v[1].tid] = dist[u.tid] + min(self.comp_matrix[v[1].tid]) + self.comm_matrix[v[1].tid][u.tid]
				tmp_v = v[1]

	final_dist = dist[len(list(list(self.graph.nodes()))) - 1]
	critical_path.append(len(list(list(self.graph.nodes()))) - 1)
	q = Queue()
	q.put(len(list(self.graph.nodes())) - 1)

	while not q.empty():
		u = q.get()
		tmp_max = 0
		for v in list(self.graph.predecessors(Task(u))):
			if dist[v.tid] > tmp_max:
				tmp_max = dist[v.tid]
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