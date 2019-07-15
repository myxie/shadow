wf = Workflow('something.graphml')
wf.load_attributes('attributes.json')

# Todo The workflow constructor will need to be edited to work with the new format



with open('heft_graph.json') as infile:
    json.load(infile)
x = json.load('heft_graph.json')
import json
x = None
with open('heft_graph.json') as infile:
    x =json.load(infile)
x
ls
x
y = None
y = {"resource": [7, 6, 11],
"data_rate":[
        [0,1,1],
                [1,0,1],
                        [1,1,0]
                            ]}
y
z = {}
z['graph']=x
z['system']=y
z
with open('final_graph_heft.json','w') as outfile:
    json.dump(z, outfile)
graph_test = None
with open('final_graph_heft.json', 'r') as infile:
    graph_test = json.load(infile)
nx
nx.readwrite.json_graph.node_link_graph(graph_test['graph'])
jsonGraph = nx.readwrite.json_graph.node_link_graph(graph_test['graph'])
