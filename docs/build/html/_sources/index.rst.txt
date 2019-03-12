.. shadow documentation master file, created by
   sphinx-quickstart on Wed Feb 20 16:08:44 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========
*shadow*
=========

.. include:: ../../README.rst

*shadow* has been designed to test the effectiveness of a vareity of algorithms
that may be used to schedule Radio Interferometry pipelines for the Square
kilometre Array (SKA). 

An example model is as follows::


	from algorithms.heuristic import heft
	from classes.workflow import Workflow

	# This workflow calculates the task time for each resource based on the
	# demand and supply vectors provided in the 'flop_rep_test.json' file. 
	wf = Workflow('topcuoglu.graphml')
	retval = wf.load_attributes('flop_rep_test.json')
	print(heft(wf))
	wf.pretty_print_allocation()


	# Original HEFT workflow; task time on reach resource is provided
	# directly by the .json file. 

	wf = Workflow('topcuoglu.graphml')
	retval = wf.load_attributes('heft.json',calc_time=False)
	print(heft(wf))
	wf.pretty_print_allocation()

The output of ``wf.pretty_print_allocation()``  looks something like this::

	0       (29, 42, '1')   (22, 40, '4')   (0, 11, '0')
	1       (60, 81, '7')                   (11, 21, '3')
	2       (84, 98, '9')                   (21, 30, '2')
	3                                       (30, 45, '5')
	4                                       (45, 55, '6')
	5                                       (58, 71, '8')
	6
	7
	8
	9
	Total Makespan: 98

.. toctree::
    :hidden:
    :glob:

    *
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
