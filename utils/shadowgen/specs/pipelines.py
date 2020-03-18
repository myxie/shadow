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
Parametric model results as derived in the Parametric model presented in
SKA-TEL-SDP-0000013
"""

from constants import SI

class PulsarSearch:
	search_parameters = {
		'no_beams': (
			1500,  # mid
			500  # low
		),
		'no_candidates_per-beam': 1000,
		'no_freq_cahnnels_per-beam': 128,
		'nu_pulse_profile_bins': 128,
		'observation_length': 600  # seconds
	}
	task_requirements = {
		'merge_oclds': (0.19*SI.giga, 30*SI.giga),  # flop, GB
		'gen_extract_heuristics': (300,000, )
	}
