# Copyright (C) 24/6/20 RW Bunney

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

# Use these functions to setup the widgets that can be used in notebooks
# to make the interaction more 'engaging'
from shadow.algorithms.heuristic import heft, pheft, fcfs
from ipywidgets import interact, widgets

w = widgets.RadioButtons(
	options=['pepperoni', 'pineapple', 'anchovies'],
	#    value='pineapple', # Defaults to 'pineapple'
	#    layout={'width': 'max-content'}, # If the items' names are long
	description='Pizza topping:',
	disabled=False
)
style = {'description_width': 'initial', 'width': 'max-content'}

g = widgets.Dropdown(
	options=[('heft', heft), ('pheft', pheft), ('fcfs', fcfs)],
	# value='pineapple', # Defaults to 'pineapple'
	# layout={'width': 'max-content'}, # If the items' names are long
	description='Heuristic selection:',
	style=style,
	disabled=False
)


def display_algorithms_options():
	options = [('heft', heft), ('pheft', pheft), ('fcfs', fcfs)],
	# value='pineapple', # Defaults to 'pineapple'
	# layout={'width': 'max-content'}, # If the items' names are long
	description = 'Heuristic selection:',
	syle = style
	widget = widgets.Dropdown()
	return (widget)


