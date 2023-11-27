import cycless.cycles as cy
import cycless.polyhed as ph
import networkx as nx

g = nx.dodecahedral_graph()

cycles = [cycle for cycle in cy.cycles_iter(g, maxsize=6)]
for polyhed in ph.polyhedra_iter(cycles):
    print(polyhed)
