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

logger = logging.getLogger(__name__)


class Environment(object):

	def __init__(self, config):
		with open(config, 'r') as infile:
			self.env = json.load(infile)
		self.has_comp = False
		self.has_mem = False
		self.has_cost = False
		self.has_rates = False

		self.num_machines = len(self.env['system']['resources'])

		if self._check_comp(self.env['system']['resources']):
			self.has_comp = True

		# machines -> categories -> machines -> compute
		self.machines = self.env['system']['resources']
		# TODO Use rates in system config; for time being rates are taken from graph
		self.rates = self.env['system']['rates']
		if self.rates:
			self.has_rates = True

		logger.debug("Environment config:\n \
					has_comp:{0}\n \
					has_mem:{1}\n \
					has_cost:{2}\n \
					has_rates:{3}\n \
					num_machines:{4}\n \
					has_comp:{5}\n \
					has_rates:{6}\n"
		)


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

	# self.en nviron['system']
	#
	#
	# self.machines = [[] for x in range(len(self.env['resource']))]
	# self.data_load = np.array([])
	# self.thrpt = 0.0
