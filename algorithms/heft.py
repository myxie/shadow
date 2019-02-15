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

# Code from deprecated HEFT implementation written by the author found at 
# https://github.com/mxyie/heft

# This is a temporary file whilst existing issues with HEFT code is ironed out.

import networkx as nx

from random import randint
from queue import Queue

from algorithms.utils import read_matrix
# from algorithms.workflow import Workflow


# graph = nx.read_graphml(graphml,int)#,Task)
# comp_matrix = read_matrix(comp)
# comm_matrix = read_matrix(comm)
# num_processors = len(self.comp_matrix[0])
# processors = [[] for x in range(0,self.num_processors)]
# # TODO have this matrix generated only when we are
# # ranking/scheduling for this particular type of thing
# oct_rank_matrix = dict()
#
# rank_sort = []
# top_sort = []


class Heft(object):
    def __init__(self, comp, comm, graphml):
        self.graph = nx.read_graphml(graphml,int)#,Task)
        self.comp_matrix = read_matrix(comp)
        self.comm_matrix = read_matrix(comm)
        self.num_processors = len(self.comp_matrix[0])
        self.processors = [[] for x in range(0,self.num_processors)] 
        # TODO have this matrix generated only when we are
        # ranking/scheduling for this particular type of thing
        self.oct_rank_matrix = dict()

        self.rank_sort = []
        self.top_sort = []

    def rank(self, method,processor=0):
        if method == 'up':
            for node in sorted(list(self.graph.nodes())):
                self.rank_up(node)
            self.rank_sort = self.rank_sort_tasks()
            self.top_sort = self.top_sort_tasks()
        
        if method == 'random':
            for node in sorted(list(self.graph.nodes())):
                self.rank_up_random(node)
            self.rank_sort = self.rank_sort_tasks()
            self.top_sort = self.top_sort_tasks()
            
        elif method == 'oct':
            for val in range(0,len(self.processors)):
                for node in sorted(list(self.graph.nodes()),reverse=True): 
                    self.rank_oct(node,val)
            
            for node in list(self.graph.nodes()):
                ave = 0
                for (n, p) in self.oct_rank_matrix:
                    if n is node:
                        ave += self.oct_rank_matrix[(n,p)]

                self.graph.nodes[node]['rank'] = ave/len(self.processors)

            self.rank_sort = self.rank_sort_tasks()
            self.top_sort = self.top_sort_tasks()
            

    def show_rank(self):

        for node in list(self.graph.nodes()):
            print (node.rank)


    def ave_comm_cost(self,node,successor):
        """
        Returns the 'average' communication cost, which is just 
        the cost in the matrix. Not sure how the ave. in the 
        original paper was calculate or represented...
            
        :params node: Starting node
        :params successor: Node with which the starting node is communicating
        """
        cost = self.comm_matrix[node][successor]
        return cost 

    def ave_comp_cost(self,tid):
        comp = self.comp_matrix[tid]
        return sum(comp)/len(comp)

    def max_comp_cost(self,tid):
        comp = self.comp_matrix[tid]
        return max(comp)

    def min_comp_cost(self, tid):
        comp = self.comp_matrix[tid]
        return min(comp)


    def rank_up(self,node):
        """
        Upward ranking heuristic outlined in Topcuoglu, Hariri & Wu (2002)
        Closely modelled off 'cal_up_rank' function at: 
        https://github.com/oyld/heft/blob/master/src/heft.py

        :param node: A task node in an DAG that is being ranked
        """
        longest_rank = 0
        for successor in self.graph.successors(node):
            if not 'rank' in self.graph.nodes[successor]: # if we have not assigned a rank
#            if successor.rank is -1:
                self.rank_up(successor)

            longest_rank = max(longest_rank, self.ave_comm_cost(node,successor)+\
                               self.graph.nodes[successor]['rank'])

        ave_comp = self.ave_comp_cost(node)
        #node.rank = ave_comp + longest_rank
        # Use node because networkx dictionary is expecting {Task(n): val} relationship 
        self.graph.nodes[node]['rank'] = ave_comp + longest_rank

    def rank_up_random(self,node):
        """
        Computes the upward rank based on either the average, max or minimum
        computational cost
        """

        longest_rank = 0
        for successor in self.graph.successors(node):
            if not 'rank' in self.graph.nodes[successor]: # if we have not assigned a rank
#            if successor.rank is -1:
                self.rank_up(successor)
            
            longest_rank = max(longest_rank, self.ave_comm_cost(node,successor)+\
                    self.graph.nodes[successor]['rank'])

        entropy = randint(0,1000)%3
        if entropy is 0:
            ave_comp = self.ave_comp_cost(node)
        elif entropy is 1:
            ave_comp = self.max_comp_cost(node)
        elif entropy is 2: 
            ave_comp = self.max_comp_cost(node)

        # node.rank = ave_comp + longest_rank
        self.graph.nodes[node]['rank'] = ave_comp + longest_rank


        return -1

    def rank_oct(self, node, pk):
        """
        Optimistic cost table ranking heuristic outlined in 
        Arabnejad and Barbos (2014)
        """
        max_successor = 0
        for successor in self.graph.successors(node):
            min_processor=1000
            for processor in range(0,len(self.processors)):
                oct_val = 0
                if (successor, processor) not in self.oct_rank_matrix.keys():
                    self.rank_oct(successor, processor) 
                comm_cost = 0
                comp_cost = self.comp_matrix[successor][processor] 
                if processor is not pk:
                    comm_cost = self.ave_comm_cost(node, successor)
                oct_val = self.oct_rank_matrix[(successor,processor)] +\
                        comp_cost+ comm_cost
                min_processor = min(min_processor,oct_val)
            max_successor = max(max_successor, min_processor)
        
        self.oct_rank_matrix[(node,pk)] = max_successor

    
    def rank_sort_tasks(self):
        """ 
        Model from this: http://stackoverflow.com/questions/403421/
        how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects

        ut.sort(key=lambda x: x.count, reverse=True)

        Sort Tasks by rank provided. According to Topcuolgu et al.(2002), 
        this is a topological order of tasks
        """
        nodes = list(self.graph.nodes())
        # nodes.sort(key=lambda x: x.rank, reverse=True)
        nodes.sort(key=lambda x: self.graph.nodes[x]['rank'],reverse=True)
        print(nodes)
        return nodes
    

    def top_sort_tasks(self):
        """
        Use networkx library built-in topological sort function to generate a sorted
        list of tasks based on precedence constraints. This is to test whether or 
        not the ranking heuristic is any better than a topological sort approach
        """
        sort_list=nx.topological_sort(self.graph)
        
        return sort_list

    def critical_path(self):
        top_sort = self.top_sort_tasks()
        dist = [-1 for x in range(len(list(self.graph.nodes())))]
        dist[0] = 0
        critical_path = []

        for u in top_sort:
            for v in list(self.graph.edges(u)):
                tmp_v = v[1]
                if dist[v[1]] < dist[u] + min(self.comp_matrix[v[1]])+ self.comm_matrix[v[1]][u]:
                    dist[v[1]] = dist[u] + min(self.comp_matrix[v[1]]) + self.comm_matrix[v[1]][u]
                    tmp_v = v[1]

        
        final_dist=dist[len(list(list(self.graph.nodes())))-1]
        critical_path.append(len(list(list(self.graph.nodes())))-1)
        q = Queue()
        q.put(len(list(self.graph.nodes()))-1)


        while not q.empty():
            u = q.get()
            tmp_max = 0
            for v in list(self.graph.predecessors(u)):
                if dist[v] > tmp_max:
                    tmp_max = dist[v]
                    tmp_v=v
                    if tmp_v not in critical_path:
                        critical_path.append(tmp_v)
                    q.put(tmp_v)
                elif dist[v] is 0:
                    tmp_v = 0 # this is the first node in the graph
                    if tmp_v not in critical_path:
                        critical_path.append(tmp_v  )
        cp_min = 0
        for x in critical_path:
            cp_min = cp_min + min(self.comp_matrix[x])

        return cp_min

    def sequential_execution(self):
        # TODO Add test case for this 
        seq = -1
        
        for p in range(len(self.processors)):
            comp = 0 
            for task in list(self.graph.nodes()):
                comp = comp + self.comp_matrix[task][p]
            if(seq is -1) or (comp < seq):
                seq = comp

        return seq
    
    def calc_est(self,node,processor_num,task_list):
        """
        Calculate the Estimated Start Time of a node on a given processor
        """
        
        est = 0 # If the node does not have predecessors
        predecessors = self.graph.predecessors(node)
        for pretask in predecessors:
            if not 'processor' in self.graph.nodes[pretask]:
                self.graph.nodes[pretask]['processor'] = 0 # Default to 0
            # If task isn't on the same processor
            if self.graph.nodes[pretask]['processor'] != processor_num: 
                comm_cost = self.comm_matrix[pretask][node]
            else:
                comm_cost = 0 # task is on the same processor, communication cost is 0

            # self.graph.predecessors is not being updated in insertion_policy;
            # need to use the tasks that are being updated to get the right results
            index = task_list.index(pretask)
            aft = self.graph.nodes[task_list[index]]['aft']
            tmp = aft  + comm_cost
            if tmp >= est:
                est = tmp

        # Now we find the time it fits in on the processor
        processor = self.processors[processor_num] # return the list of allocated tasks
        available_slots = []
        if len(processor) == 0:
            return est # Nothing in the time slots yet 
        else:
            for x in range(len(processor)):
                # For each start/finish time tuple that exists in the processor
                if x == 0:
                    if processor[0][0] != 0: #If the start time of the first tuple is not 0
                        available_slots.append((0,processor[0][0]))# add a 0-current_start time tuple
                    else:
                        continue
                else: 
                    # Append the finish time of the previous slot and the start time of this slot
                    available_slots.append((processor[x-1][1],processor[x][0]))
            
            # Add a very large number to the final time slot available, so we have a gap after 
            available_slots.append((processor[len(processor)-1][1],-1))
            if node==1 and processor_num==2:
                print(available_slots)

        for slot in available_slots:
            if est < slot[0] and slot[0] + self.comp_matrix[node][processor_num] <= slot[1]:
                return slot[0]
            if (est >= slot[0]) and (est + \
                    self.comp_matrix[node][processor_num]<=slot[1]): 
               return est 
            # At the 'end' of available slots
            if (est >= slot[0]) and (slot[1]<0):
                return est 
            # This last case occurs when we have a low est but a high cost, so
            # it doesn't fit in any gaps; hence we have to put it at the 'end'
            # and start it late
            if (est < slot[0]) and (slot[1]<0):
                return slot[0] 

        return est
    
    def insertion_policy(self,option=None):
        """
        Allocate tasks to processors following the insertion based policy outline 
        in Tocuoglu et al.(2002)
        """
        # TODO The tasks below are from a list, not the global graph; so we do
        # a lot of checking of both the list and the graph to get information. 
        # Need to figure out a cleaner way of dealing with this. 
        makespan = 0
        for task in self.rank_sort:
            if task == self.rank_sort[0]: 
                w = min(self.comp_matrix[task])
                p = self.comp_matrix[task].index(w)
                self.graph.nodes[task]['processor'] = p
                self.graph.nodes[task]['ast'] = 0
                self.graph.nodes[task]['aft'] = w
                self.processors[p].append((self.graph.nodes[task]['ast'],\
                                           self.graph.nodes[task]['ast'],\
                                           str(task)))
            else:
                aft = -1 # Finish time for the current task
                p = 0 
                for processor in range(self.num_processors):
                    # tasks in self.rank_sort are being updated, not self.graph;
                    est = self.calc_est(task, processor,self.rank_sort)
                    if aft == -1: # assign initial value of aft for this task
                        aft = est + self.comp_matrix[task][processor]
                        p = processor
                    # see if the next processor gives us an earlier finish time
                    elif est + self.comp_matrix[task][processor] < aft:
                        aft = est + self.comp_matrix[task][processor]
                        p = processor
    
                self.graph.nodes[task]['processor'] = p
                self.graph.nodes[task]['ast'] = aft - self.comp_matrix[task][p]
                self.graph.nodes[task]['aft'] = aft
                if self.graph.nodes[task]['aft'] >= makespan:
                   makespan  = self.graph.nodes[task]['aft']
                self.processors[p].append((self.graph.nodes[task]['ast'],\
                                           self.graph.nodes[task]['aft'],\
                                           str(task)))
                self.processors[p].sort(key=lambda x: x[0])
            #print(self.processors)

        return makespan


    def insertion_policy_oct(self):
        """
        Allocate tasks to processors following the insertion based policy outline 
        in Tocuoglu et al.(2002)
        """

        makespan = 0
        if not self.oct_rank_matrix:
            self.rank('oct')
        eft_matrix = dict()
        oeft_matrix = dict()
        p=0
        for task in self.rank_sort:
            if task == self.rank_sort[0]:
                self.graph.nodes[task]['ast'] = 0
                min_oeft = -1
                for processor in range(self.num_processors):
                    eft_matrix[(task,processor)] = self.comp_matrix[task][processor]
                    oeft_matrix[(task,processor)] = eft_matrix[(task,processor)]\
                                                    + self.oct_rank_matrix[(task,processor)]
                    if (min_oeft == -1) or \
                            (oeft_matrix[(task,processor)]  < min_oeft): 
                        min_oeft = oeft_matrix[(task,processor)]
                        p = processor
                        
                self.graph.nodes[task]['aft'] = self.comp_matrix[task][p]
                self.graph.nodes[task]['processor'] = p
                self.processors[p].append((self.graph.nodes[task]['ast'],\
                                           self.graph.nodes[task]['aft'],\
                                           str(task)))

            else:
                min_oeft = -1
                for processor in range(self.num_processors):
                    if self.graph.predecessors(task):
                        est = self.calc_est(task,processor,self.rank_sort)
                    else:
                        est=0
                    eft = est + self.comp_matrix[task][processor]
                    eft_matrix[(task,processor)] = eft
                    oeft_matrix[(task,processor)] = eft_matrix[(task,processor)]\
                        + self.oct_rank_matrix[(task,processor)]
                    if (min_oeft ==-1) or \
                            (oeft_matrix[(task,processor)]  < min_oeft): 
                        min_oeft = oeft_matrix[(task,processor)]
                        p = processor

                self.graph.nodes[task]['aft'] =  eft_matrix[(task,p)]  
                self.graph.nodes[task]['ast'] = self.graph.nodes[task]['aft']\
                                                - self.comp_matrix[task][processor]
                self.graph.nodes[task]['processor'] = p

                if self.graph.nodes[task]['aft'] >= makespan:
                    makespan = self.graph.nodes[task]['aft']
                    
                self.processors[p].append((self.graph.nodes[task]['ast'],\
                                           self.graph.nodes[task]['aft'],\
                                           str(task)))
                self.processors[p].sort(key=lambda x: x[0]) 

        return makespan

    def schedule(self, schedule='insertion'):
        if schedule is 'insertion':
            retval = self.insertion_policy()
        elif schedule is 'oct_schedule':
            retval = self.insertion_policy_oct()

        return retval

    def display_schedule(self):
        retval = self.insertion_policy() 
        return retval
        

  
