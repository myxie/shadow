import networkx as nx
import math
from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models.graphs import from_networkx

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import GraphRenderer, StaticLayoutProvider, Oval
from bokeh.palettes import Spectral8

G=nx.karate_club_graph()

plot = figure(title="Networkx Integration Demonstration", x_range=(-1.1,1.1), y_range=(-1.1,1.1),
              tools="", toolbar_location=None)

#graph = from_networkx(G, nx.random_layout)
nodes = list(G.nodes())
graph = GraphRenderer()

graph.node_renderer.data_source.add(nodes, 'index')
graph.node_renderer.data_source.add(Spectral8, 'color')
graph.node_renderer.glyph = Oval(height=0.1, width=0.2, fill_color='color')

start = []
end = []
for edge in G.edges():
    start.append(edge[0])
    end.append(edge[1])

graph.edge_renderer.data_source.data = dict(
    start= start,
    end=end)

## start of layout code
circ = [i*2*math.pi/8 for i in nodes]
x = [math.cos(i) for i in circ]
y = [math.sin(i) for i in circ]
graph_layout = dict(zip(nodes, zip(x, y)))
graph.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)
#
plot.renderers.append(graph)

output_file("networkx_graph.html")
show(plot)