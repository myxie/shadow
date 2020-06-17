# Copyright (C) 17/6/20 RW Bunney

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

# This is adapted and expanded upon in the shadowgen.ipynb notebook



from shadow.models.workflow import Workflow
from shadow.models.environment import Environment
import shadow.algorithms.heuristic as heuristic

workflow = Workflow('dax_files/output/shadow_Epigenomics_24.json')
env = Environment('environments/sys.json')
workflow.add_environment(env)
heuristic.heft(workflow)



