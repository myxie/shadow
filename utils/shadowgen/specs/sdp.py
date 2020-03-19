# Copyright (C) 16/3/20 RW Bunney

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
Contains the specifications and details for the SDP hardware outlined in SKA­TEL­SDP­0000091

https://www.microway.com/knowledge-center-articles/detailed-specifications-intel-xeon-e5-2600v3-haswell-ep-processors/
Based on the above link, the Galaxy Ivy Bridge has 8FLOPs/Cycle
"""
from utils.constants import SI

SKALOW_nodes = 896
SKAMID_nodes = 786
gpu_per_node = 2
gpu_peak_flops = 31 * SI.tera # Douple precision
memory_per_node = 31 * SI.giga

SKALOW_buffer_size = 67 * SI.peta
SKAMID_buffer_size = 116 * SI.peta
SKALOW_buffer_storage_per_node = 75 * SI.tera
SKAMID_buffer_storage_per_node = 147 * SI.tera
SKALOW_storage_per_island = 4.2 * SI.peta
SKAMID_storage_per_island = 7.7 * SI.peta

