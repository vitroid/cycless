#!/usr/bin/env python3
"""
Here is a sample program to decompose a hydrogen bond network into cycles.
It is as close as possible to the one used in the paper, but it is slightly different from the code used in the actual analysis.
"""

import numpy as np
import networkx as nx

# for a directed graph

class DiCycles(nx.DiGraph):
    """
    A collection of methods for directed cycles.

    The edges of the digraph may contain its spatial orientation in the "vec" attribute. In that case, _find algorithm avoids a transversing (spanning) cycle in the periodic orthogonal cell. "vec" must be specified in the fractional coordinate. (The distance between the opposing surfaces is 1.)
    """
    def __init__(self, data=None, vec=False):
        super().__init__(data)
        self.vec = vec


    def _find(self, history, size):
        """
        Recursively find a homodromic cycle.

        No shortcut is allowed.

        The label of the first vertex in the history (head) must be the smallest.
        """
        head = history[0]
        last = history[-1]
        if len(history) == size:
            for next in self.successors(last):
                if next == head:
                    # test the dipole moment of a cycle.
                    d = np.zeros(3)
                    if self.vec:
                        for i in range(len(history)):
                            a,b = history[i-1], history[i]
                            d += self[a][b]["vec"]
                        if np.allclose(d, np.zeros(3)):
                            yield tuple(history)
                    else:
                        yield tuple(history)
        else:
            for next in self.successors(last):
                if next < head:
                    # Skip it;
                    # members must be greater than the head
                    continue
                if next not in history:
                    # recurse
                    yield from self._find(history+[next], size)


    def all_iter(self, size):
        """
        List the cycles of the size only. No shortcuts are allowed during the search.
        """
        for head in self.nodes():
            yield from self._find([head], size)







def test():
    import random
    random.seed(1)
    dg = nx.DiGraph()
    # a lattice graph of 4x4x4
    X,Y,Z = np.meshgrid(np.arange(4.0), np.arange(4.0), np.arange(4.0))
    X = X.reshape(64)
    Y = Y.reshape(64)
    Z = Z.reshape(64)
    coord = np.array([X,Y,Z]).T
    # fractional coordinate
    coord /= 4
    for a in range(64):
        for b in range(a):
            d = coord[b] - coord[a]
            # periodic boundary condition
            d -= np.floor(d+0.5)
            # if adjacent
            if d @ d < 0.3**2:
                # orient randomly
                if random.randint(0,1) == 0:
                    dg.add_edge(a,b,vec=d)
                else:
                    dg.add_edge(b,a,vec=-d)
    # PBC-compliant
    dc = DiCycles(dg, vec=True)
    A = set([cycle for cycle in dc.all_iter(4)])
    print(f"Number of cycles (PBC compliant): {len(A)}")
    print(A)

    # not PBC-compliant
    dc = DiCycles(dg)
    B = set([cycle for cycle in dc.all_iter(4)])
    print(f"Number of cycles (crude)        : {len(B)}")
    print(B)

    # difference
    C = B - A
    print("Cycles that span the cell:")
    print(C)


if __name__ == "__main__":
    test()
