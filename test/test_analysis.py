# Copyright (C) 26/6/20 RW Bunney

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

import unittest

from shadow.models.workflow import Workflow
from shadow.models.environment import Environment
from utils.analysis import metrics
from shadow.algorithms.heuristic import heft, fcfs

import test.config as cfg
import logging
import os

logging.basicConfig(level=1)
logger = logging.getLogger(__name__)

@unittest.skip
class TestMetrics(unittest.TestCase):

	def setUp(self) -> None:
		logger.debug("{0}".format(os.getcwd()))
		self.workflow = Workflow(cfg.test_analysis_data['workflow'])
		self.env = Environment(cfg.test_analysis_data['environment'])
		self.workflow.add_environment(self.env)

	def test_speedup(self):
		val = metrics.speedup(self.workflow)
		# We haven't scheduled the workflow yet
		self.assertEqual(-1, val)
		soln = heft(workflow=self.workflow)
		heftval = metrics.speedup(self.workflow)
		fcworkflow = Workflow(cfg.test_analysis_data['workflow'])
		fcworkflow.add_environment(self.env)
		soln = fcfs(fcworkflow)
		fcval = metrics.speedup(fcworkflow)
		logger.debug("{0}>{1}".format(heftval, fcval))
		self.assertGreater(heftval, fcval)

	def test_efficiency(self):
		soln = heft(workflow=self.workflow)
		efficiency = metrics.efficiency(self.workflow)
		logger.debug("{0}".format(efficiency))
		fcworkflow = Workflow(cfg.test_analysis_data['workflow'])
		fcworkflow.add_environment(self.env)
		soln = fcfs(fcworkflow)
		fcval = metrics.efficiency(fcworkflow)
		logger.debug("{0}>{1}".format(efficiency,fcval))

