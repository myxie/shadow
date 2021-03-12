# Copyright (C) 31/7/20 RW Bunney

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See  the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Generate a homoegneous cluster of 10 nodes
"""
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

from utils.shadowgen import generator
HETEROGENEITY = [1.0]  # Homogeneous
NUM_MACHINES = 400
SPEC_RANGE = [(50,100)]
MAGNITUDE = 'giga'

SYSTEM_OUTPUT_PATH = 'recipes/routput/basic_spec-{0}.json'.format(
    NUM_MACHINES
)
system_config_path = generator.generate_system_machines(
    SYSTEM_OUTPUT_PATH, NUM_MACHINES, MAGNITUDE, HETEROGENEITY, SPEC_RANGE
)
logger.info(system_config_path)
