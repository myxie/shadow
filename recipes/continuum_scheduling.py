# Copyright (C) 20/1/21 RW Bunney

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
Let's see how long it takes to schedule a small continuum pipline,
where small means 15,621 nodes. We will be scheduling this on a 'cluster'
with 40 machines.
"""

from shadow.models.workflow import Workflow
from shadow.models.environment import Environment
from shadow.algorithms.heuristic import heft, fcfs


WORKFLOW = "routput/shadow_Continuum_ChannelSplit.json"
CLUSTER = "routput/system_spec_40_200-400_1.0"

wf_fcfs = Workflow(WORKFLOW)
env_fcfs = Environment(CLUSTER)
wf_fcfs.add_environment(env_fcfs)

wf_heft = Workflow(WORKFLOW)
env_heft = Environment(CLUSTER)
wf_heft.add_environment(env_heft)

soln = fcfs(wf_fcfs)
print(soln.makespan)

soln2 = heft(wf_heft)
print(soln2.makespan)
