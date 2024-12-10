# cycless

A collection of algorithms to analyze a graph as a set of cycles.

Some codes come from [https://github.com/vitroid/Polyhed](vitroid/Polyhed) and [https://github.com/vitroid/countrings](vitroid/countrings) are integrated and improved.

## API

API manual is [here](https://vitroid.github.io/cycless).


## cycles.py

A simple algorithm to enumerate all irreducible cycles of n-members and smaller in an undirected graph. [Matsumoto 2007]

```python
import cycless.cycles as cy
import networkx as nx

g = nx.cubical_graph()

for cycle in cy.cycles_iter(g, maxsize=6):
    print(cycle)
```

## dicycles.py

An algorithm to enumerate the directed cycles of a size in a dircted graph. [Matsumoto 2021]

```python
from genice2.genice import GenIce
from genice2.plugin import Lattice, Format, Molecule
import cycless.dicycles as dc

# Generate an ice I structure as a directed graph
lattice = Lattice("1h")
formatter = Format("raw", stage=(3,))
raw = GenIce(lattice, signature="ice 1h", rep=[2, 2, 2]).generate_ice(formatter)

for cycle in dc.dicycles_iter(raw["digraph"], size=6):
    print(cycle)
```

## polyhed.py

An algorithm to enumerate the quasi-polyhedral hull made of cycles in an undirected graph. A quasi-polyhedral hull (vitrite) obeys the following conditions: [Matsumoto 2007]

1. The surface of the hull is made of irreducible cycles.
2. Two or three cycles shares a vertex of the hull.
3. Two cycles shares an edge of the hull.
4. Its Euler index (F-E+V) is two.

```python
import cycless.cycles as cy
import cycless.polyhed as ph
import networkx as nx

g = nx.dodecahedral_graph()

cycles = [cycle for cycle in cy.cycles_iter(g, maxsize=6)]
for polyhed in ph.polyhedra_iter(cycles):
    print(polyhed)
```

## simplex.py

Enumerate triangle, tetrahedral, and octahedral subgraphs found in the given graph.

## References

1. M. Matsumoto, A. Baba, and I. Ohmine, Topological building blocks of hydrogen bond network in water, J. Chem. Phys. 127, 134504 (2007). http://doi.org/10.1063/1.2772627
2. Matsumoto, M., Yagasaki, T. & Tanaka, H. On the anomalous homogeneity of hydrogen-disordered ice and its origin. J. Chem. Phys. 155, 164502 (2021). https://doi.org/10.1063/5.0065215
