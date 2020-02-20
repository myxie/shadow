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
import unittest
from test.test_config import test_environment_data
import os
from shadow.classes.environment import Environment
# Tests for /algorithms/heuristic.py


# Testing heft algorithms in heuristics.py

class TestEnvironmentInit(unittest.TestCase):
	def setUp(self) -> None:
		print(os.listdir('.'))
		self.env = Environment(test_environment_data['environment_sys'])
		pass

	def test_init(self):
		self.assertTrue(self.env.has_comp)

	def tearDown(self) -> None:
		pass

