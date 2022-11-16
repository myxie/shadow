# Copyright (C) 2018 RW Bunney

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


import json
import sys
import operator
import logging

import networkx as nx
import numpy as np
from shadow.models.environment import Environment
from shadow.models.solution import Solution

LOGGER = logging.getLogger(__name__)


# TODO clean up allocation and ranking;
#  reduce direct  to the graph,
#  instead, only interact with
#  workflow tasks, naccessot graph nodes

class Task(object):
    """
    Tasks are components of a Workflow that store information associated to
    their compute requirement.
    """

    def __init__(self, tid, flops=0, data=None, pre_compute=False):
        self.tid = tid  # task id - this is unique
        self.rank = -1  # This is updated during the 'Task Prioritisation' phase
        self.pre_compute = pre_compute
        # Resource usage
        self.flops_demand = flops  # Will use the constants
        self.io_demand = data
        # Following is {machine name, value} dictionary pairs
        if self.pre_compute:
            self._calculated_runtime = {}
            self._calculated_io = {}
            self._calculated_memory = {}
        # allocations
        self.machine = None
        self.ast = 0  # actual start time
        self.aft = 0  # actual finish time  # if self.pre_compute:  #  #  #
        # self.test_runtime = self._calculated_runtime  # else:  #  #  #
        # self.test_runtime = {}

    def __repr__(self):
        return str(self.tid)

    #
    # Node must be hashable for use with networkx
    def __hash__(self):
        return hash(self.tid)

    def __eq__(self, task):
        if isinstance(task, self.__class__):
            return self.tid == task.tid

    def __lt__(self, task):
        if isinstance(task, self.__class__):
            return self.tid < task.tid

    def __le__(self, task):
        if isinstance(task, self.__class__):
            return self.tid <= task.tid

    def calc_runtime(self, machine):
        if self.pre_compute:
            return self._calculated_runtime[machine]
        else:
            # Sometimes we may have data but the divisor is more of an issue.
            if machine.iorate:
                data = int(np.round(self.io_demand / machine.iorate))
            else:
                data = 0
            compute = int(np.round(self.flops_demand / machine.flops))
            return max(compute,
                       data)  # return  # self.calculated_runtime[machine]

    def calculated_runtime(self, machine):
        if self.pre_compute:
            return self._calculated_runtime[machine]
        else:
            # if self.test_runtime[machine] != self.calc_runtime(machine):
            #     raise RuntimeError('Incorrect calculation')
            return self.calc_runtime(machine)

    def calc_ave_runtime(self, env):
        if self.pre_compute:
            return (sum(self._calculated_runtime.values()) / len(
                self._calculated_runtime))
        else:
            mcompute = np.array([m.flops for m in env.machines])
            miorate = np.array([m.iorate for m in env.machines])
            compute = self.flops_demand / mcompute
            if miorate.any():
                data = self.io_demand / miorate
            else:
                data = 0
            return max(np.average(np.round(compute).astype(int)),
                       np.average(np.round(data).astype(int)))

    def calc_mininum_runtime(self, env):
        """
        Find the minimum runtime for this task in the `env` Environment

        This is acheived by finding the machine with the largest flops,
        iorate etc., and then using this value as the denominator for the
        time calculation

        Parameters
        ----------
        env :
            The environment variable that we are concerned with scheduling

        Returns
        -------
        machine, time pairing

        Notes
        ------
        Whilst we want to find the minimal runtime on all machines, when we
        compare the compute time to the io time, we want to pick the largest
        of the two - this is because the largest value demonstrates which
        element is the bottleneck for this task.

        """
        if self.pre_compute:
            return min(self._calculated_runtime.items(),
                       key=operator.itemgetter(1))
        else:
            cm = max(env.machines, key=operator.attrgetter('flops'))
            cw = int(np.round(self.flops_demand / cm.flops))
            if cm.iorate:
                iow = int(np.round(self.io_demand / cm.iorate))
                return cm, max(iow, cw)
            else:
                return cm, cw  # return compute, w

    def calc_max_runtime(self, env):
        if self.pre_compute:
            return max(self._calculated_runtime.items(),
                       key=operator.itemgetter(1))
        else:
            compute = min(env.machines, key=operator.attrgetter('flops'))
            w = int(np.round(self.flops_demand / compute.flops))
            return compute, w

    def update_task_rank(self, rank):
        self.rank = rank

    def allocate_task(self, machine_id):
        self.machine = machine_id
        pass


class Workflow(object):
    """
    Workflow class acts as a wrapper for all things associated with a task
    workflow

    :param config: JSON formatted file that stores the structural \
    information of the underlying workflow graph. See utils.shadowgen for more \
    information on producing shadow-compatible JSON files.

    The workflow includes this is a test
    """

    def __init__(self, config, taskobj=Task, from_file=True):
        """
        """
        with open(config, 'r') as infile:
            wfconfig = json.load(infile)
        self.graph = nx.readwrite.json_graph.node_link_graph(wfconfig['graph'])
        self._time = wfconfig['header']['time']
        # Take advantage of how pipelines
        mapping = {}
        for node in self.graph.nodes:
            precompute = False
            if self._time:
                precompute = True
            comp = self.graph.nodes[node]['comp']
            if 'data' in self.graph.nodes[node]:
                data = self.graph.nodes[node]['data']
            else:
                data = 0
            t = taskobj(node, comp, data, precompute)
            mapping[node] = t
        self.graph = nx.relabel_nodes(self.graph, mapping, copy=False)
        self.tasks = self.graph.nodes
        self.edges = self.graph.edges

        # Initialised when we 'add_environment'
        self.env = None
        # Solution is dependent on an environment
        self.solution = None

        # This lets us know when reading the graph if 'comp' attribute  # in
        # the Networkx graph is time or FLOPs based

    def add_environment(self, environment):
        """
        :param environment: An environment object using the Environment class. \
        This should be created first, then added to the Workflow.
        :return: Non-negative return value inidcates success.
        """
        self.env = environment
        # Go through environment flags and check what processing we can do
        # to the workflow
        self.solution = Solution(machines=[m for m in self.env.machines])
        # That is, the runtime of tasks has already been calculated
        if self._time:
            # Check the number of  values stored for each node so they match the
            # nunber of machines in thcomputatione system config
            for task in self.tasks:
                try:
                    comp_array_length = len(self.tasks[task]['comp'])
                except TypeError:
                    print("Computation costs should be an array, "
                          "but instead is {0}. Check your configuration "
                          "files".format(self.tasks[task]['comp']))
                    raise TypeError
                if len(self.tasks[task]['comp']) is not len(self.env.machines):
                    raise RuntimeError
                machines = [m for m in self.env.machines]
                runtime_list = self.tasks[task]['comp']
                task._calculated_runtime = dict(zip(machines, runtime_list))
                task.test_runtime = task._calculated_runtime
            return 0
        # Use compute provided by system values to calculate the time taken
        else:
            LOGGER.debug('Tasks do not have pre calculated runtimes')
            # for m in self.env.machines:
            #     for task in self.tasks:
            #         comp = task.flops_demand
            # task.test_runtime[m] = int(
            #     self.env.calc_task_runtime_on_machine(m, comp)
            # )
            return 0

    def sort_tasks(self, sort_type):
        """
        Sorts task in a task wf based on a specified sort_type

        :params task_wf - Wf that has tasks to be sorted
        :params sort_type - How we sort the tasks (topological, task rank etc.)
        """

        if sort_type == 'rank':
            return sorted(self.tasks, key=lambda x: x.rank, reverse=True)

        if sort_type == 'topological':
            return nx.topological_sort(self.graph)
        else:
            raise NotImplementedError(
                "This sorting method has not been implemented")

    def solution_exec_order(self):
        return sorted(self.tasks, key=lambda x: x.ast)
