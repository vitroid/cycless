from logging import getLogger
from methodtools import lru_cache
import itertools

import numpy as np
import networkx as nx



def centerOfMass(members, rpos):
    logger = getLogger()
    dsum = np.zeros(3)
    for member in members:
        d = rpos[member] - rpos[members[0]]
        d -= np.floor(d+0.5)
        dsum += d
    com = rpos[members[0]] + dsum / len(members)
    com -= np.floor(com)
    return com



# Modified from CountRings class in gtihub/vitroid/countrngs
class Cycles(nx.Graph):
    def __init__(self, data=None, pos=None):
        super(Cycles, self).__init__(data)
        # self.dist    = dict()
        # fractional coordinate in a orthogonal cell in numpy array
        self.pos     = pos


    #shortes_pathlen is a stateless function, so the cache is useful to avoid re-calculations.
    @lru_cache(maxsize=None)
    def _shortest_pathlen(self, pair):
        return len(nx.shortest_path(self, *pair)) - 1


    def _shortcuts( self, members ):
        n = len(members)
        for i in range(0,n):
            for j in range(i+1,n):
                d = min(j-i, n-(j-i))
                if d > self._shortest_pathlen(frozenset((members[i],members[j]))):
                    return True
        return False


    def _findring( self, members, max ):
        #print members, "MAX:", max
        if len(members) > max:
            return (max, [])
        s = set(members)
        last = members[-1]
        results = []
        for adj in self[last]:
            if adj in s:
                if adj == members[0]:
                    #Ring is closed.
                    #It is the best and unique answer.
                    if not self._shortcuts( members ):
                        return (len(members), [members])
                else:
                    #Shortcut ring
                    pass
            else:
                (newmax,newres) = self._findring( members + [adj], max )
                if newmax < max:
                    max = newmax
                    results = newres
                elif newmax == max:
                    results += newres
        return (max, results)


    def _is_spanning(self, cycle):
        "Return True if the cycle spans the periodic cell."
        sum = np.zeros_like(self.pos[cycle[0]])
        for i in range(len(cycle)):
            d = self.pos[cycle[i-1]] - self.pos[cycle[i]]
            d -= np.floor(d+0.5)
            sum += d
        return np.any(np.absolute(sum) > 1e-5)



    def cycles_iter( self, maxsize ):
        """
        A generator of cycles in a graph.
        """
        logger = getLogger()
        rings = set()
        for x in self:
            neis = sorted(self[x])
            for y,z in itertools.combinations(neis, 2):
                triplet = [y,x,z]
                (max, results) = self._findring( triplet, maxsize )
                for i in results:
                    #Make i immutable for the key.
                    j = frozenset(i)
                    #and original list as the value.
                    if j not in rings:
                        # logger.debug("({0}) {1}".format(len(i),i))
                        if self.pos is None or not self._is_spanning(i):
                            yield tuple(i)
                            rings.add(j)


def test():
    g = nx.DiGraph()
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
                g.add_edge(a,b)
    # PBC-compliant
    c = Cycles(g, pos=coord)
    A = set([cycle for cycle in c.cycles_iter(4)])
    print(f"Number of cycles (PBC compliant): {len(A)}")
    print(A)

    # not PBC-compliant
    c = Cycles(g)
    B = set([cycle for cycle in c.cycles_iter(4)])
    print(f"Number of cycles (crude)        : {len(B)}")
    print(B)

    # difference
    C = B - A
    print("Cycles that span the cell:")
    print(C)


if __name__ == "__main__":
    test()
