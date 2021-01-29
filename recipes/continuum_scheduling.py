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

import pandas as pd
import seaborn as sns


from shadow.models.workflow import Workflow
from shadow.models.environment import Environment
from shadow.algorithms.heuristic import heft, fcfs


df = pd.DataFrame(columns=["time", "channels","algorithm","diff"])
WORKFLOW = "routput/shadow_Continuum_ChannelSplit_10.json"
CLUSTER = "routput/system_spec_40_200-400_1.0"

wf_fcfs = Workflow(WORKFLOW)
env_fcfs = Environment(CLUSTER)
wf_fcfs.add_environment(env_fcfs)
soln = fcfs(wf_fcfs)
seq = -1

#
# for p in range(len(self.processors)):
#     comp = 0
#     for task in list(self.graph.nodes()):
#         comp = comp + self.comp_matrix[task.tid][p]
#     if (seq is -1) or (comp < seq):
#         seq = comp

for x in range(10, 100, 10):
    print("Scheduling {0} Channels".format(x))
    WORKFLOW = "routput/shadow_Continuum_ChannelSplit_{0}.json".format(x)
    CLUSTER = "routput/system_spec_40_200-400_1.0"

    wf_fcfs = Workflow(WORKFLOW)
    env_fcfs = Environment(CLUSTER)
    wf_fcfs.add_environment(env_fcfs)

    wf_heft = Workflow(WORKFLOW)
    env_heft = Environment(CLUSTER)
    wf_heft.add_environment(env_heft)

    soln = fcfs(wf_fcfs)
    fcfs_res = soln.makespan

    soln2 = heft(wf_heft)
    heft_res = soln2.makespan
    diff = abs(fcfs_res-heft_res)
    values = {"time": fcfs_res, "channels": x, "algorithm": "fcfs",
              "diff":diff}
    row_to_add = pd.Series(values, name=x)
    df = df.append(row_to_add)
    values = {"time": heft_res, "channels": x, "algorithm": "heft",
              "diff":diff}
    row_to_add = pd.Series(values, name=x)
    df = df.append(row_to_add)

print(df)
df.to_pickle("continuum_pickle.pkl")
sns.set_style("darkgrid")
df.time = df.time.astype(float)
df.channels=df.channels.astype(float)
import matplotlib.pyplot as plt
sns.lineplot(x="channels", y="time", hue="algorithm", data=df)
plt.show()
plt.savefig("channels.png")