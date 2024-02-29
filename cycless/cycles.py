from logging import getLogger
from methodtools import lru_cache
import itertools
from typing import Generator
import heapq

import numpy as np
import networkx as nx

# for pDoc3
__all__ = ["cycles_iter"]


def centerOfMass(members, rpos):
    # logger = getLogger()
    dtotal = np.zeros(3)
    origin = rpos[list(members)[0]]
    for member in members:
        d = rpos[member] - origin
        d -= np.floor(d + 0.5)
        dtotal += d
    com = rpos[members[0]] + dtotal / len(members)
    com -= np.floor(com)
    return com


# Modified from CountRings class in gtihub/vitroid/countrngs
def cycles_iter(
    graph: nx.Graph, maxsize: int, pos: np.ndarray = None
) -> Generator[tuple, None, None]:
    """
    The function `cycles_iter` is a generator that finds all cycles in an undirected graph up to a    specified maximum size, and optionally checks if the cycles span a periodic cell based on fractional    coordinates of the nodes.

    Args:
      graph (nx.Graph): The `graph` parameter is an undirected graph represented using the `nx.Graph`    class from the NetworkX library. It represents the connections between nodes in the graph.
      maxsize (int): The `maxsize` parameter in the `cycles_iter` function represents the maximum size    of a cycle that the generator will yield. It determines the length of the cycles that the function    will search for in the graph.
      pos (np.ndarray): The `pos` parameter is an optional argument that represents the fractional    coordinates of the nodes in the graph. It is a numpy array of shape (n, m), where n is the number of    nodes in the graph. Each row in the array represents the fractional coordinates of a node in the    graph.
    """

    def shortest_paths(G, start, end, exclude=set(), maxedges=999999):
        """
        Find all shortests paths from the start to end.

        Returns:
        list of shortest paths from the start to one of the ends.
        """
        q = [
            (
                0,
                [
                    start,
                ],
            )
        ]  # Heap of (cost, path)
        cheapest = maxedges
        while len(q):
            # logger.debug(q)
            (cost, path) = heapq.heappop(q)
            if cost > cheapest:
                break
            v0 = path[-1]
            if v0 == end:
                cheapest = cost  # first arrived
                yield path
            else:
                if v0 in exclude:
                    continue
                exclude.add(v0)
                for v1 in G[v0]:
                    if v1 not in exclude:
                        heapq.heappush(q, (cost + 1, path + [v1]))

    # shortes_pathlen is a stateless function, so the cache is useful to avoid
    # re-calculations.
    @lru_cache(maxsize=None)
    def _shortest_pathlen(graph, pair):
        return len(nx.shortest_path(graph, *pair)) - 1

    def _shortcuts(graph, members):
        n = len(members)
        for i in range(0, n):
            for j in range(i + 1, n):
                d = min(j - i, n - (j - i))
                if d > _shortest_pathlen(graph, frozenset((members[i], members[j]))):
                    return True
        return False

    def _is_spanning(cycle):
        "Return True if the cycle spans the periodic cell."
        total = np.zeros_like(pos[cycle[0]])
        N = len(cycle)
        for i, j in zip(cycle[-1 : N - 1], cycle):
            d = pos[i] - pos[j]
            d -= np.floor(d + 0.5)
            total += d
        return np.any(np.absolute(total) > 1e-5)

    logger = getLogger()
    rings = set()
    for x in graph:
        neis = sorted(graph[x])
        for y, z in itertools.combinations(neis, 2):
            results = []
            for cycle in shortest_paths(graph, z, y, {x}, maxedges=maxsize - 2):
                members = [x] + cycle
                assert cycle[0] == z and cycle[-1] == y
                if not _shortcuts(graph, members):
                    results.append(members)
            for i in results:
                # Make i immutable for the key.
                j = frozenset(i)
                # and original list as the value.
                if j not in rings:
                    # logger.debug("({0}) {1}".format(len(i),i))
                    if pos is None or not _is_spanning(i):
                        yield tuple(i)
                        rings.add(j)


# def graph_overlap(g1, g2):
#     """
#     Return the common part of two graphs.
#
#     They are adjacent if two subgraphs share at least one vertex.
#     """
#     # common vertices
#     common = g1.nodes() and g2.nodes()
#     g = nx.Graph()
#     for v in common:
#         g.add_node(v)
#     if len(common) > 0:
#         # common edges
#         for e in g1.edges():
#             if g2.has_edge(*e):
#                 g.add_edge(*e)
#     return g


def test():
    g = nx.Graph()
    # a lattice graph of 4x4x4
    X, Y, Z = np.meshgrid(np.arange(4.0), np.arange(4.0), np.arange(4.0))
    X = X.reshape(64)
    Y = Y.reshape(64)
    Z = Z.reshape(64)
    coord = np.array([X, Y, Z]).T
    # fractional coordinate
    coord /= 4
    for a in range(64):
        for b in range(a):
            d = coord[b] - coord[a]
            # periodic boundary condition
            d -= np.floor(d + 0.5)
            # if adjacent
            if d @ d < 0.3**2:
                g.add_edge(a, b)
    # PBC-compliant
    A = set([cycle for cycle in cycles_iter(g, 4, pos=coord)])
    print(f"Number of cycles (PBC compliant): {len(A)}")
    print(A)

    # not PBC-compliant
    B = set([cycle for cycle in cycles_iter(g, 4)])
    print(f"Number of cycles (crude)        : {len(B)}")
    print(B)

    # difference
    C = B - A
    print("Cycles that span the cell:")
    print(C)

    # g1 = nx.Graph([(1,2),(2,3),(3,4)])
    # g2 = nx.Graph([(1,4)])
    # print(graph_overlap(g1,g2))


if __name__ == "__main__":
    test()
