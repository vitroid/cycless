# cycless

A collection of algorithms to analyze a graph as a set of cycles.

Some codes come from [https://github.com/vitroid/Polyhed](vitroid/Polyhed) and [https://github.com/vitroid/countrings](vitroid/countrings) are integrated and improved.

## API

API manual is [here]({{project.urls.manual}}).

## Cycles

A simple algorithm to enumerate all irreducible cycles of n-members and smaller in an undirected graph. [Matsumoto 2007]

```python
{% include "samples/cycles.py" %}
```

### Counting policy

- It counts only irreducible rings (rings not having shortcut bridges).
- It counts rings purely topologically. It does not use geometrical information.
- Edge direction is not considered. (Undirected graph)

### Algorithm

1. Choose 3 successive nodes (i.e. two adjacent acyclic edges) along the network. (King's criteria) [King1991]
1. Find the smallest rings passing the three nodes.
1. The ring must not have shotcuts, i.e. path connecting two vertices on the ring which is shorter than the path along the ring. (Using Dijkstra's algorithm.) (Franzblau's SP ring criteria) [Franzblau1991]
1. Put the ring in the list.
1. Repeat 1 .. 4 until all sets of 3 successive nodes are tested.
1. Eliminate the permutations of a ring in the list.
1. (Optional) Remove "crossing rings".

So, our definition is a hybrid of the algorithms of King and Franzblau.

### Note

- Our definition is different from Franzblau's SP ring. Our algorithm does not count the 6-membered rings in a cubic graph but counts the geodesic 4-membered rings in a regular octahedral graph. [Franzblau1991]
- Our definition is different from King's K ring. [King1991]
- Our definition is different from Goetzke's strong ring. We do not care the strength. [Goetzke1991]
- Our definition is different from that of Camisasca's. They count too much 5-membered rings. [Camisasca2019]
- Probably somebody has already made the same definition. Let me know if you find that.

### To Cite It

- M. Matsumoto, A. Baba, and I. Ohmine, Topological building blocks of hydrogen bond network in water, J. Chem. Phys. 127, 134504 (2007); [doi:10.1063/1.2772627](http://dx.doi.org/doi:10.1063/1.2772627)

## Dicycles

An algorithm to enumerate the directed cycles of a size in a dircted graph. [Matsumoto 2021]

```python
{% include "samples/dicycles.py" %}
```

### To Cite It

- Matsumoto, M., Yagasaki, T. & Tanaka, H. On the anomalous homogeneity of hydrogen-disordered ice and its origin. J. Chem. Phys. 155, 164502 (2021); [doi:10.1063/5.0065215](https://doi.org/10.1063/5.0065215)

## Polyhed

An algorithm to enumerate the quasi-polyhedral hull made of cycles in an undirected graph. A quasi-polyhedral hull (vitrite) obeys the following conditions: [Matsumoto 2007]

1. The surface of the hull is made of irreducible cycles.
2. Two or three cycles shares a vertex of the hull.
3. Two cycles shares an edge of the hull.
4. Its Euler index (F-E+V) is two.

```python
{% include "samples/polyhed.py" %}
```

### To Cite It

- M. Matsumoto, A. Baba, and I. Ohmine, Topological building blocks of hydrogen bond network in water, J. Chem. Phys. 127, 134504 (2007); [doi:10.1063/1.2772627](http://dx.doi.org/doi:10.1063/1.2772627)

## Simplex

Enumerate triangle, tetrahedral, and octahedral subgraphs found in the given graph.

## Rings

In this module, a directed graph whose underlying undirected graph is a cycle is defined as a Ring. Along the ring, a bit string representing whether each directed edge is oriented forward or backward is defined as a code. `rings.py` provides a set of functions for computing statistics of codes.

```python
{% include "samples/rings.py" %}
```

### To Cite It

- Matsumoto, M., Yagasaki, T. & Tanaka, H. GenIce-core: Efficient algorithm for generation of hydrogen-disordered ice structures. J. Chem. Phys. 160, 094101 (2024).

## References

- Camisasca, G., Schlesinger, D., Zhovtobriukh, I., Pitsevich, G. & Pettersson, L. G. M. A proposal for the structure of high- and low-density fluctuations in liquid water. J. Chem. Phys. 151, 034508 (2019).
- Downs, G. M., Gillet, V. J., Holliday, J. D. & Lynch, M. F. Review of ring perception algorithms for chemical graphs. J. Chem. Inf. Comput. Sci. 29, 172–187 (1989).
- Franzblau, D. S. Computation of ring statistics for network models of solids. Phys. Rev. B 44, 4925–4930 (1991).
- Goetzke, K. & Klein, H. J. Properties and efficient algorithmic determination of different classes of rings in finite and infinite polyhedral networks. J. Non-Cryst. Solids. 127, 215–220 (1991).
- KING, S. V. Ring Configurations in a Random Network Model of Vitreous Silica. Nature 213, 1112–1113 (1967).
- Marians, C. S. & Hobbs, L. W. Network properties of crystalline polymorphs of silica. J. Non-Cryst. Solids. 124, 242–253 (1990).
- M. Matsumoto, A. Baba, and I. Ohmine, Topological building blocks of hydrogen bond network in water, J. Chem. Phys. 127, 134504 (2007). http://doi.org/10.1063/1.2772627
- Matsumoto, M., Yagasaki, T. & Tanaka, H. On the anomalous homogeneity of hydrogen-disordered ice and its origin. J. Chem. Phys. 155, 164502 (2021). https://doi.org/10.1063/5.0065215
- Matsumoto, M., Yagasaki, T. & Tanaka, H. GenIce-core: Efficient algorithm for generation of hydrogen-disordered ice structures. J. Chem. Phys. 160, 094101 (2024).
