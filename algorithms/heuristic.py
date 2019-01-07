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

# This file contains code for implementing heuristic-based scheduling
# algorithms. Currently, this file implements the following algorithms:
# * HEFT 
# * PHEFT 

import time

import networkx as nx

from algorithms.workflow import Workflow

"""
HEFT ranking and allocation functionality
"""

def rank_tasks(wf, method):
    """
    Ranks tasks according to the specified method. Tasks need to be ranked,
    then sorted according to the rank. Returns a sorted list of tasks in
    order of rank. 
    :params task_list - The list of tasks to be ranked
    :params method - Ranking method (e.g. upward rank, optimistic cost table)
    """

    if method == 'up':
        for node in sorted(list(wf.nodes())):
            rank_up(wf,node)
            
        rank_sort = rank_sort_tasks()
        top_sort =  top_sort_tasks()

    if method == 'random':
        for node in sorted(list(wf.nodes())):
            rank_up_random(node)
        rank_sort = rank_sort_tasks()
        top_sort = top_sort_tasks()

    elif method == 'oct':
        for val in range(0,len(self.processors)):
            for node in sorted(list(wf.nodes()),reverse=True): 
                rank_oct(node,val)

        for node in list(wf.nodes()):
            ave = 0
            for (n, p) in oct_rank_matrix:
                if n is node:
                    ave += oct_rank_matrix[(n,p)]

            wf.nodes[node]['rank'] = ave/len(processors)

        rank_sort = rank_sort_tasks()
        top_sort = top_sort_tasks()

    return rank_sort, top_sort


def rank_up(wf,node):
    """
    Upward ranking heuristic outlined in Topcuoglu, Hariri & Wu (2002)
    Closely modelled off 'cal_up_rank' function at: 
    https://github.com/oyld/heft/blob/master/src/heft.py
    
    :param wf - Subject workflow
    :param node -  A task node in an DAG that is being ranked
    """
    longest_rank = 0
    for successor in wf.successors(node):
    if not 'rank' in wf.nodes[successor]: # if we have not assigned a rank
        rank_up(successor)

    longest_rank = max(longest_rank, ave_comm_cost(node,successor)+\
                       wf.nodes[successor]['rank'])

    ave_comp = ave_comp_cost(node)
    wf.nodes[node]['rank'] = ave_comp + longest_rank

def rank_up_random(wf,node):
    """
    Computes the upward rank based on either the average, max or minimum
    computational cost
    """

    longest_rank = 0
    for successor in wf.successors(node):
        if not 'rank' in self.wf.nodes[successor]: # if we have not assigned a rank
#            if successor.rank is -1:
            self.rank_up(successor)

        longest_rank = max(longest_rank, ave_comm_cost(node,successor)+\
                self.wf.nodes[successor]['rank'])

    randval = randint(0,1000)%3
    if randval is 0:
        ave_comp = self.ave_comp_cost(node)
    elif randval is 1:
        ave_comp = self.max_comp_cost(node)
    elif randval is 2: 
        ave_comp = self.max_comp_cost(node)

    # node.rank = ave_comp + longest_rank
    wf.nodes[node]['rank'] = ave_comp + longest_rank


def rank_oct(wf, node, pk):
    """
    Optimistic cost table ranking heuristic outlined in 
    Arabnejad and Barbos (2014)
    """
    max_successor = 0
    for successor in wf.successors(node):
        min_processor=1000
        for processor in range(0,len(processors)):
            oct_val = 0
            if (successor, processor) not in self.oct_rank_matrix.keys():
                self.rank_oct(successor, processor) 
            comm_cost = 0
            comp_cost = comp_matrix[successor][processor] 
            if processor is not pk:
                comm_cost = ave_comm_cost(node, successor)
            oct_val = oct_rank_matrix[(successor,processor)] +\
                    comp_cost+ comm_cost
            min_processor = min(min_processor,oct_val)
        max_successor = max(max_successor, min_processor)

    self.oct_rank_matrix[(node,pk)] = max_successor


def sort_tasks(wf, sort_type):
    """
    Sorts task in a task wf based on a specified sort_type
    
    :params task_wf - Wf that has tasks to be sorted 
    :params sort_type - How we sort the tasks (topological, task rank etc.)
    """
    
    if sort_type == 'rank':
        tasks = list(wf.nodes())
        return tasks.sort(key=lambda x: wf.nodes[x]['rank'],\
                          reverse=True)
    if sort_type == 'topological':
        return nx.topological_sort(wf)
    else:
        return None

   

