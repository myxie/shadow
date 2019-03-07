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

# This file contains code for implementing metaheuristic scheduling algorithms.
# Currently, this file implements the following algorithms:
# 


# TODO; initial setup required for a genetic algorithm
# TODO; initial setup required for an evolutionary algorithm 6

"""
From Yu, Kirley & Buyya 2007
NSGAII* and SPEAII*: 
1. Generate intial population
do:
    2. crossover on individuals
    3. perform mutation on offspring
    4. evaluate current solutions
    5. select individuals to be carried onto next generation
while(termination condition not satisfied)

The two differ on evaluation and selection strategy
"""

def nsga2(wf,seed): 
    generate_population(wf,seed)

    """
    Whilst we have not reached our terminal condition, do: 
        crossover on individual solutions
        mutate the offspring
        evaluate the quality of the solutions
        select individuals to carry over to the new population
    """
    return None


def spea2(wf,seed): 
    generate_population(wf,seed)
    return None


def generate_population(wf,seed):
    pop = []
    """
    task_assign[0] is the resource to which Task0 is assigned
    exec_order[0] is the task that will be executed first

    each 'solution' should be a tuple of a task-assign and exec-order solution
    
    In the future it might be useful, in addition to checking feasibility of solution, to minimise duplicates of the population generated. Not sure about this. 

    """
    task_assign = [] 
    exec_order = []

    return pop

def is_feasibility(task_order):
    """
    Check that task_order is a valid topological sort
    """
    return True

def crossover(soln):
    """
    As described in Yu & Buyya 2007

    Two step approach: 
    1. Two parents are selected at random from population
    2. Two random points are selected from the task-assignment strings
    3. all tasks between the points are chosen as crossover points
    4. the service allocation of the tasks within the crossover points are exchanged. 
    """
    return None

def mutation(soln):
    return None


def cost_fitness():
    return None

def time_fitness():
    return None

def throughput_fitness():
    return None

def reliability_fitness():
    return None

