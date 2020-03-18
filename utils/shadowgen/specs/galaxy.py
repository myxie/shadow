# Copyright (C) 12/3/20 RW Bunney

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

"""
Contains the specifications and details for the hardware used in Pawsey's "Galaxy"
HPC facility. 
https://www.microway.com/knowledge-center-articles/detailed-specifications-intel-xeon-e5-2600v3-haswell-ep-processors/
Based on the above link, the Galaxy Ivy Bridge has 8FLOPs/Cycle
"""

from constants import SI


class XeonIvyBridge:
	# Based
	flops_per_cycle = 8
	ncycles = 3.0 * SI.giga  # frequency e.g. 2.2GHz
	bandwidth = 0
	memory = 0

