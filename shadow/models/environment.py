# Copyright (C) 2019 RW Bunney

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
import sys
import json
import logging

from shadow.models.globals import *

logger = logging.getLogger(__name__)


class Machine(object):
	def __init__(self, mid, flops, cost, bandwidth):
		self.id = mid
		self.machine_type = mid.split("_")[0]
		self.flops = flops
		self.cost = cost
		self.bandwidth = bandwidth


def _process_env_resources(resources ):
	if resources is None:
		raise EnvironmentError("Environment is not appropriately defined")
	else:
		machines = []
		# This is resources dictionary
		for machine in resources:
			name = machine
			flops, memory, bandwidth = None, None, None
			if 'flops' in resources[machine]:
				flops = resources[machine]['flops']
			if 'memory' in resources[machine]:
				memory = resources[machine]['memory']
			if 'bandwidth' in resources[machine]:
				bandwidth = resources[machine]['bandwidth']
			m = Machine(name, flops, memory, bandwidth)
			machines.append(m)
		return machines


class Environment(object):
	def __init__(self, config):
		with open(config, 'r') as infile:
			jdict = json.load(infile)

		resources, rates, cost = None, None, None
		if ENV_RESOURCE in jdict[ENV_SYS]:
			resources = jdict[ENV_SYS][ENV_RESOURCE]
		if ENV_RATES in jdict[ENV_SYS]:
			rates = jdict[ENV_SYS][ENV_RATES]
		if ENV_COST in jdict[ENV_SYS]:
			cost = jdict[ENV_SYS][ENV_COST]

		self.machines = _process_env_resources(resources)
		self.rates = rates
		self.cost = cost


	def _check_comp(self, res_dict):
		"""
		Sanity check for computation values in the resources part of our system spec
		:param res_dict: The 'resources' sub-dictionary from our json file
		:return: True if data is correct
		"""
		retval = None
		for machine in res_dict:
			tmp_flops_val = None
			# This is a sanity check to ensure that each machine category has machines with the same computing capacity
			machine_dict = res_dict[machine]
			if 'flops' in machine_dict:
				retval = True
			else:
				# sys.exit('Error: We need some form of computation provision in our system config')
				retval = False
				return retval
			if tmp_flops_val is None:
				tmp_flops_val = machine_dict['flops']
			else:
				if tmp_flops_val != machine_dict['flops']:
					# sys.exit('Error: The computing power of machines in the same category are different.')
					return retval
		return retval

	def parse_environment_config(self, dictionary):
		"""

		:param dictionary:
		:return:
		"""
		return None

	def _check_cost(self, res_dict):
		retval = False
		return retval

	def calc_task_runtime_on_machine(self, machine, task_flops):
		"""
		returns Task runtime based on total Floating point operations required to complete the task
		:param machine: the machine on which the task is being run
		:param task_flops: the total number of FLOPs in the task
		:return:
		"""
		return int(np.round(task_flops / machine.flops))

	def calc_task_cost_on_machine(self, machine, task_runtime):
		"""
		Machine costs are presented as $ per second
		:param machine: Machine on which the task is running
		:param task_runtime: the total runtime of the task
		:return: The total cost in $ of running the task on the
		"""
		machine_type_prefix = machine.machine_type
		return self.cost[machine_type_prefix] * task_runtime

	def calc_data_transfer_time(self, data_size):
		average_rate = sum(self.rates.values())/len(self.rates.values())
		return int(data_size/average_rate)




# self.en nviron['system']
#
#
# self.machines = [[] for x in range(len(self.env['resource']))]
# self.data_load = np.array([])
# self.thrpt = 0.0
