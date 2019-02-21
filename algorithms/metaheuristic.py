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
    return None


def spea2(wf,seed): 
    generate_population(wf,seed)
    return None


def generate_population(wf,seed):
    pop = []
    """
    task_assign[0] is the resource to which Task0 is assigned
    exec_order[0] is the task that will be executed first
    """
    task_assign = [] 
    exec_order = []

    return pop

def execution_feasibility(task_order):
    # Check that task_order is a valid topological sort
    return True

def crossover(soln):
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

