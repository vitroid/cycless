import cycless.cycles as cy
import networkx as nx

g = nx.cubical_graph()

for cycle in cy.cycles_iter(g, maxsize=6):
    print(cycle)
