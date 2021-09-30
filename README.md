# cycless

A collection of algorithms to analyze a graph as a set of cycles.

Some codes come from [https://github.com/vitroid/Polyhed](vitroid/Polyhed) and [https://github.com/vitroid/countrings](vitroid/countrings) are integrated and improved.

## cycles.py

A simple algorithm to enumerate all irreducible cycles of n-members and smaller in an undirected graph. [Matsumoto 2007]

## dicycles.py

An algorithm to enumerate the irreducible cycles of a size in a dircted graph. [Matsumoto 2021]

## polyhed.py

An algorithm to enumerate the quasi-polyhedral hull made of cycles in an undirected graph. A quasi-polyhedral hull (vitrite) obeys the following conditions: [Matsumoto 2007]

1. The surface of the hull is made of irreducible cycles.
2. Two or three cycles shares a vertex of the hull.
3. Two cycles shares an edge of the hull.
4. Its Euler index (F-E+V) is two.

## References

1. M. Matsumoto, A. Baba, and I. Ohmine, Topological building blocks of hydrogen bond network in water, J. Chem. Phys. 127, 134504 (2007). http://doi.org/10.1063/1.2772627
2. Masakazu Matsumoto, Takuma Yagasaki, Hideki Tanaka et al. Hyperhomogeneity of hydrogen-disordered ice and its origin: the residual entropy compatible with the disparity in hydrogen bond energy, 22 January 2021, PREPRINT (Version 1) available at Research Square [https://doi.org/10.21203/rs.3.rs-143208/v1]
