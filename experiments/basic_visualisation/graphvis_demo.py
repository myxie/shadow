# Copyright (C) 26/6/20 RW Bunney

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
from shadow.models.workflow import Workflow
from shadow.models.environment import Environment
import shadow.visualiser.graph as sgraph
from IPython.display import Image

workflow_file = 'TestAskapCont_channels-10_shadow.json'
sys = 'final_heft_sys.json'
workflow = Workflow(workflow_file)
env = Environment(sys)
workflow.add_environment(env)

# png = sgraph.visualise_graph(workflow, workflow_file.strip('.json')+'.png')

graphviz = sgraph.convert_to_graphviz(workflow)
graphviz.render('output.gz')
