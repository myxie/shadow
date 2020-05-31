# Copyright (C) 2020 RW Bunney

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


class Allocation:
	"""
	A simple storage class to save an allocation to a solution
	"""

	def __init__(self, task, machine):
		self.tid = task.tid
		self.ast = task.ast
		self.aft = task.aft


class Solution:
	"""
	A solution is generated by an algorithm, or a number of solutions are generated
	in the case that we are comparing a population of solutions.
	"""

	def __init__(self, machines):
		self.machines = machines
		# Generate a list of allocations for each machine
		self.allocations = {m: [] for m in machines}
		self.execution_order = []
		self.makespan = 0

	def _is_feasible(self, task_order):
		"""
		Check that task_order is a valid topological sort
		"""
		return True

	def add_allocation(self, task, machine):
		a = Allocation(task, machine)
		self.allocations[machine].append(a)
		self.allocations[machine].sort(
			key=lambda alloc: alloc.ast
		)
		self.execution_order.append(a)
		self.execution_order.sort(key=lambda alloc: alloc.ast)

	def list_machine_allocations(self, machine):
		"""
		Returns a sorted list of the current Allocation objects being stored on
		the machine
		:param machine: The String name of the machine
		:return:
		"""
		self.allocations[machine].sort(
			key=lambda alloc: alloc.ast
		)
		return self.allocations[machine]

	def list_all_allocations(self):
		return self.allocations

	def find_alloc(self, task):
		pass
	def remove_allocation(self, tid, m):
		pass
