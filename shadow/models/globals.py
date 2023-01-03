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

"""
Globals in shadow are useful variables that access dictionary attributes without the
uuser having to remember what the attribute strings are. This is especially useful given that
configuration data in shadow is described in JSON files, and JSON maps very well to Python
dictionaries. Unfortunately, this means users do not get access to linting or class-variable
help in their chosen editors/IDEs, because the dictionary key is not reserved or accesible.
"""

ENV_SYS = 'system'
ENV_RESOURCE = 'resources'
ENV_RATES = "compute_bandwidth"
ENV_BANDWIDTH = 'system_bandwidth'
ENV_COST = 'cost'

WORKFLOW_DATASIZE = 'transfer_data'
