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

########################################################################

"""
This module contais code for implementing heuristic-based scheduling
algorithms. Currently, this file implements the following algorithms:

* HEFT 
* PHEFT 
"""
from random import randint
import networkx as nx
import operator
import copy
from shadow.models.solution import Solution
from collections import deque

RANDMAX = 1000


#############################################################################
############################# HUERISTICS  ###################################
#############################################################################

def heft(workflow):
    """
    Implementation of the original HEFT algorithm, Topcuolgu 2002.

    :params workflow: The workflow object to schedule
    :returns: The Solution object generated by the algorithm
    """

    if workflow.env is None:
        raise RuntimeError("Workflow environment is not initialised")
    task_ranks = calculate_upward_ranks(workflow)
    for task in workflow.tasks:
        task.rank = task_ranks[task]
    solution = insertion_policy(workflow)
    return solution


def pheft(workflow):
    """
    Implementation of the PHEFT algorithm, which adaptst the HEFT algorithm
    using the concpet of an Optimistic Cost Table (OCT)
    """
    oct_rank_matrix = generate_ranking_matrix(workflow)
    # Rank tasks according to the oct_rank_matrix
    for task in workflow.tasks:
        total = 0
        for (t, p) in oct_rank_matrix:
            if t is task:
                total += oct_rank_matrix[(t, p)]

        rank = int(total / len(workflow.env.machines))
        task.rank = rank

    solution = insertion_policy_oct(workflow, oct_rank_matrix)
    return solution


def fcfs(workflow, greedy=True, seed=None):
    if workflow.env is None:
        raise RuntimeError("Workflow environment is not initialised")
    solution = fcfs_allocation(workflow, greedy, seed)
    return solution


def minimin(workflow):
    """Real-Time Task Mapping and Scheduling for Collaborative
    In-Network Processingin DVS-Enabled Wireless Sensor Networks"""
    pass


def hlfet(workflow):
    pass


def mapping(workflow):
    pass


# TODO: Partial Critical Paths
def pcp(workflow):
    return None


# TODO: Multi-objective list scheduling
def mols(workflow):
    return None


#############################################################################
############### HELPER FUNCTIONS & HEURISTIC-SPECIFIC POLICIES ##############
#############################################################################

def generate_ranking_matrix(workflow):
    """
    Optimistic cost table ranking heuristic outlined in
    Arabnejad and Barbos (2014)
    """
    oct_rank_matrix = {}
    stack = deque()
    for task in sorted(list(workflow.tasks)):
        for machine in workflow.env.machines:
            if (task, machine) not in oct_rank_matrix.keys():
                stack.append((task, machine))

    while len(stack) > 0:
        (curr_task, pk) = stack.pop()
        max_successor = 0
        for successor in workflow.graph.successors(curr_task):
            min_machine = 1000
            for machine in workflow.env.machines:
                comp_cost = successor.calculated_runtime[machine]
                comm_cost = 0
                if machine is not pk:
                    comm_cost = ave_comm_cost(workflow, curr_task, successor)
                oct_val = oct_rank_matrix[(successor, machine)] \
                          + comp_cost \
                          + comm_cost
                min_machine = min(min_machine, oct_val)

            max_successor = max(max_successor, min_machine)
        oct_rank_matrix[(curr_task, pk)] = max_successor

    return oct_rank_matrix


def calculate_upward_ranks(workflow):
    """
    Upward ranking heuristic outlined in Topcuoglu, Hariri & Wu (2002)
    Closely modelled off 'cal_up_rank' function at:
    https://github.com/oyld/heft/blob/master/src/heft.py

    Ranks individual tasks and then allocates this final value
    to the attribute of the workflow graph

    :param workflow - Subject workflow
    :param task -  A task task in an DAG that is being ranked
    """

    # task = list(workflow.graph.nodes)
    # if len(list(workflow.graph.sucessors(task))) == 0:
    #     return ave_comm_cost( wf, task, successor)

    task_ranks = {}
    unranked = [node for node in workflow.graph.nodes()]

    for node in workflow.graph.nodes():
        longest_rank = 0
        if len(list(workflow.graph.successors(node))) == 0:
            task_ranks[node] = node.calc_ave_runtime() + longest_rank
            unranked.remove(node)

    while unranked:
        for node in unranked:
            longest_rank = 0
            succs = list(workflow.graph.successors(node))
            if all(k in task_ranks for k in succs):
                for s in succs:
                    if longest_rank == 0:
                        longest_rank = ave_comm_cost(
                            workflow, node, s
                        ) + task_ranks[s]
                    else:
                        longest_rank = max(
                            longest_rank, ave_comm_cost(workflow, node, s)
                            + task_ranks[s]
                        )

            if longest_rank > 0:
                task_ranks[node] = longest_rank + node.calc_ave_runtime()
                unranked.remove(node)


    return task_ranks


def ave_comm_cost(workflow, task, successor):
    data_size = workflow.graph.edges[task, successor]['data_size']
    # return workflow.graph.edges[task, successor]['data_size']

    return workflow.env.calc_data_transfer_time(data_size=data_size)


def ave_comp_cost(workflow, task):
    comp = workflow.tasks[task]['comp']
    return sum(comp) / len(comp)


def max_comp_cost(workflow, task):
    comp = workflow.tasks[task]['comp']
    return max(comp)


def min_comp_cost(workflow, task):
    comp = workflow.tasks[task]['comp']
    return min(comp)


def calc_est(workflow, task, machine, solution):
    """
    Calculate the Estimated Start Time of a task on a given processor
    """

    est = 0
    predecessors = workflow.graph.predecessors(task)
    for pretask in predecessors:
        # If task isn't on the same processor, there is a transfer cost
        alloc = solution.task_allocations[pretask]
        pre_machine_alloc = alloc.machine
        # rate = workflow.system['data_rate'][pre_processor][machine]
        if pre_machine_alloc != machine:  # and rate > 0:
            comm_cost = int(
                workflow.graph.edges[pretask, task]['data_size'])  # / rate)
        else:
            comm_cost = 0

        aft = alloc.aft
        tmp = aft + comm_cost
        if tmp >= est:
            est = tmp

    machine_str = machine
    curr_allocations = solution.list_machine_allocations(machine_str)
    available_slots = []
    num_alloc = len(curr_allocations)
    prev = None
    if len(curr_allocations) > 0:
        for i, alloc in enumerate(curr_allocations):
            if i == 0:
                if alloc.ast != 0:  # If the start time of the first allocation is not 0
                    available_slots.append((0, alloc.ast))
                else:
                    continue
            else:
                prev_alloc = curr_allocations[i - 1]
                available_slots.append((
                    prev_alloc.aft,
                    alloc.ast
                ))
        final_alloc = curr_allocations[
            num_alloc - 1]  # We want the finish time of the latest allocation.
        available_slots.append((final_alloc.aft, -1))

    for slot in available_slots:
        (start, end) = slot
        if est < start and start \
                + task.calc_runtime(machine) <= end:
            return start
        if (est >= start) and est + task.calculated_runtime[machine] <= end:
            return est
        # At the 'end' of available slots
        if (est >= start) and (end < 0):
            return est
        # This last case occurs when we have a low est but a high cost, so
        # it doesn't fit in any gaps; hence we have to put it at the 'end'
        # and start it late
        if (est < start) and (end < 0):
            return start

    return est


def insertion_policy(workflow):
    """
    Allocate tasks to machines following the insertion based policy outline
    in Tocuoglu et al.(2002)
    """
    makespan = 0
    # tasks = sort_tasks(workflow, 'rank')
    sorted_tasks = workflow.sort_tasks('rank')
    # tmp = workflow.tasks
    solution = Solution(workflow.env.machines)
    for task in sorted_tasks:
        # Treat the first task differently, as it's the easiest to get the lowest cost
        if task == list(workflow.tasks)[0]:  # Convert networkx NodeView to list
            m, w = min(
                task.calculated_runtime.items(),
                key=operator.itemgetter(1)
            )
            ast = 0
            aft = w
            solution.add_allocation(task=task, machine=m, ast=ast, aft=aft)
        else:
            aft = -1  # Finish time for the current task
            m = 0
            for machine in workflow.env.machines:
                # tasks in self.rank_sort are being updated, not workflow.graph;
                est = calc_est(workflow, task, machine, solution)
                if aft == -1:  # assign initial value of aft for this task
                    aft = est + task.calc_runtime(machine)
                    m = machine
                # see if the next processor gives us an earlier finish time
                elif est + task.calc_runtime(machine) < aft:
                    aft = est + task.calc_runtime(machine)
                    m = machine
            ast = aft - task.calc_runtime(m)

            if aft >= makespan:
                makespan = aft

            solution.add_allocation(task=task, machine=m, ast=ast, aft=aft)

    solution.makespan = makespan
    return solution


def insertion_policy_oct(workflow, oct_rank_matrix):
    """
    Allocate tasks to machines following the insertion based policy outline
    in Tocuoglu et al.(2002)
    """

    makespan = 0
    if not oct_rank_matrix:
        oct_rank_matrix = generate_ranking_matrix(workflow)
    eft_matrix = dict()
    oeft_matrix = dict()
    m = None
    sorted_tasks = workflow.sort_tasks('rank')
    solution = Solution(workflow.env.machines)
    for task in sorted_tasks:
        if task == list(workflow.tasks)[0]:
            ast = 0
            min_oeft = -1
            for machine in workflow.env.machines:
                eft_matrix[(task, machine)] = task.calculated_runtime[machine]
                oeft_matrix[(task, machine)] = \
                    eft_matrix[(task, machine)] + oct_rank_matrix[
                        (task, machine)]
                if (min_oeft == -1) or (
                        oeft_matrix[(task, machine)] < min_oeft):
                    min_oeft = oeft_matrix[(task, machine)]
                    m = machine
            aft = task.calculated_runtime[m]
            solution.add_allocation(task=task, machine=m, ast=ast, aft=aft)
        else:
            min_oeft = -1
            for machine in workflow.env.machines:
                if workflow.graph.predecessors(task):
                    est = calc_est(workflow, task, machine, solution)
                else:
                    est = 0
                eft = est + task.calculated_runtime[machine]
                eft_matrix[(task, machine)] = eft
                oeft_matrix[(task, machine)] = \
                    eft_matrix[(task, machine)] + oct_rank_matrix[
                        (task, machine)]
                if (min_oeft == -1) or (
                        oeft_matrix[(task, machine)] < min_oeft):
                    min_oeft = oeft_matrix[(task, machine)]
                    m = machine

            aft = eft_matrix[(task, m)]
            ast = aft - task.calculated_runtime[m]
            task.machine = m

            if aft >= makespan:
                makespan = aft
            solution.add_allocation(task=task, machine=m, ast=ast, aft=aft)

    solution.makespan = makespan
    return solution


def fcfs_allocation(workflow, greedy, seed):
    makespan = 0
    # tasks = sort_tasks(workflow, 'rank')
    sorted_tasks = workflow.sort_tasks("topological")
    # tmp = workflow.tasks
    solution = Solution(workflow.env.machines)
    for task in sorted_tasks:
        pred = list(workflow.graph.predecessors(task))
        if len(pred) == 0:
            start_time = 0
            m, w = min(
                task.calculated_runtime.items(),
                key=operator.itemgetter(1)
            )
            machine_available = _check_machine_availability(solution, m,
                                                            start_time, task)
            if machine_available:
                ast = start_time
                aft = w
                machine = m
                solution.add_allocation(task, machine, ast=ast, aft=aft)
        else:
            latest_predecessor_allocation = latest_allocation(task, solution,
                                                              workflow)
            earliest_start_time = -1
            finish_time = 0
            machine = latest_predecessor_allocation.machine
            machine_available = False
            earliest_start_time, finish_time, machine, machine_available = attempt_allocation_on_resource(
                workflow,
                latest_predecessor_allocation,
                solution,
                task,
                machine,
                earliest_start_time,
                finish_time,
                machine_available
            )
            if not machine_available:
                # Take the next available one
                for m in workflow.env.machines:
                    avail = _machine_earliest_availability(solution, m)
                    earliest_start_time, finish_time, machine = find_earliest_availability(
                        m,
                        task,
                        machine,
                        earliest_start_time,
                        avail,
                        finish_time
                    )
            ast = earliest_start_time
            aft = finish_time
            if aft > makespan:
                makespan = aft
            solution.add_allocation(task, machine, ast=ast, aft=aft)

    solution.makespan = makespan
    return solution


# TODO address control flow if predecessor doesn't exist due to multiple
#  head nodes

def latest_allocation(task, solution, workflow):
    pred = list(workflow.graph.predecessors(task))
    pred.sort(key=lambda x: x.aft, reverse=True)
    task_allocations = [alloc for alloc in
                        list(solution.task_allocations.values())]
    if len(task_allocations) < 1:
        xx = 1
    pred_task_allocations = [alloc for alloc in task_allocations if
                             alloc.task in pred]
    pred_task_allocations.sort(key=lambda alloc: alloc.aft, reverse=True)
    return pred_task_allocations[0]  # pred[0]


def find_earliest_availability(m, task, machine, earliest_start_time, new_start,
                               finish_time):
    # machine = latest_predecessor_allocation.machine
    if earliest_start_time == -1 or earliest_start_time > new_start:
        earliest_start_time = new_start
        finish_time = earliest_start_time + task.calculated_runtime[m]
        machine = m

    return earliest_start_time, finish_time, machine


def attempt_allocation_on_resource(workflow, latest_predecessor_allocation,
                                   solution, task, machine,
                                   earliest_start_time,
                                   finish_time, available):
    for m in workflow.env.machines:
        new_start = latest_predecessor_allocation.aft
        if m is not latest_predecessor_allocation.machine:
            data_size = \
                workflow.graph.edges[latest_predecessor_allocation.task, task][
                    'data_size']
            new_start += workflow.env.calc_data_transfer_time(data_size)
        if _check_machine_availability(solution, m, new_start, task):
            available = True
            earliest_start_time, finish_time, machine = find_earliest_availability(
                m, task, machine,
                earliest_start_time, new_start,
                finish_time)

    return earliest_start_time, finish_time, machine, available


# TODO return next available time
def _machine_earliest_availability(solution, machine):
    last_alloc = solution.latest_allocation_on_machine(machine)
    return last_alloc.aft


def _check_machine_availability(solution, machine, start_time, task):
    for alloc in solution.list_machine_allocations(machine):
        if alloc.ast <= start_time < alloc.aft:
            return False
        # if it starts beforehand but will over-run:
        if start_time < alloc.ast <= start_time + task.calc_runtime(machine):
            return False

    return True
