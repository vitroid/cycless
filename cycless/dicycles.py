#!/usr/bin/env python3

import numpy as np
import networkx as nx

# for a directed graph

def dicycles_iter(digraph, size, vec=False):
    """
    List the cycles of the size only. No shortcuts are allowed during the search.

    If vec is True and the orientations of the vectors is included in the attributes of the edges, the spanning cycles are avoided.
    """


    def _find(digraph, history, size):
        """
        Recursively find a homodromic cycle.

        No shortcut is allowed.

        The label of the first vertex in the history (head) must be the smallest.
        """
        head = history[0]
        last = history[-1]
        if len(history) == size:
            for next in digraph.successors(last):
                if next == head:
                    # test the dipole moment of a cycle.
                    d = np.zeros(3)
                    if vec:
                        for i in range(len(history)):
                            a,b = history[i-1], history[i]
                            d += digraph[a][b]["vec"]
                        if np.allclose(d, np.zeros(3)):
                            yield tuple(history)
                    else:
                        yield tuple(history)
        else:
            for next in digraph.successors(last):
                if next < head:
                    # Skip it;
                    # members must be greater than the head
                    continue
                if next not in history:
                    # recurse
                    yield from _find(digraph, history+[next], size)


    for head in digraph.nodes():
        yield from _find(digraph, [head], size)







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
    A = set([cycle for cycle in dicycles_iter(dg, 4, vec=True)])
    print(f"Number of cycles (PBC compliant): {len(A)}")
    print(A)

    # not PBC-compliant
    B = set([cycle for cycle in dicycles_iter(dg, 4)])
    print(f"Number of cycles (crude)        : {len(B)}")
    print(B)

    # difference
    C = B - A
    print("Cycles that span the cell:")
    print(C)


if __name__ == "__main__":
    test()
