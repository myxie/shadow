# SHADOW
[![Build Status](https://travis-ci.com/myxie/shadow.svg?branch=master)](https://travis-ci.com/myxie/shadow)
[![Coverage Status](https://coveralls.io/repos/github/myxie/shadow/badge.svg?branch=master)](https://coveralls.io/github/myxie/shadow?branch=master)

ScHeduling Algorithms for DAG-Workflows (SHADOW)

SHADOW is a library for the use and testing of DAG-based workflow scheduling algorithms. SHADOW provides implementations of various heuristic and metaheuristic algorithms to address single-and multi-objective scheduling problems; these algorithms are accessed using a workflow-oriented class system built into the library.

SHADOW also comes with a command-line interface that allow you to run these algorithms on pipelines from your terminal, with schedule-reporting and visualisation options. 

Documentation for shadow is available at [Read the Docs](https://shadowscheduling.readthedocs.io/), or in the `docs/` directory.

SHADOW is being actively developed by [Ryan Bunney](https://www.icrar.org/people/rbunney/), a PhD Candidate at the [International Centre for Radio Astronomy Research (ICRAR)](https://www.icrar.org/), in Perth, Western Australia. 

## Dependencies 

SHADOW is built on the following libraries;
 
* Networkx
* NumPy
* Matplotlib
* Graphviz

Networkx forms the backbone of the Workflow objects that are used to interface with the scheduling algorithms. NumPy is used for efficient array calculations, and matplotlib and Graphviz for plotting and graph visualisation, respectively. 
