#!/usr/bin/env python3
#
# Simplified from github/Vitrite

import sys
from collections import defaultdict
from logging import getLogger
from typing import Generator

import networkx as nx
import numpy as np

from cycless.cycles import cycles_iter

# for pDoc3
__all__ = ["polyhedra_iter"]


def cage_to_graph(cage, ringlist):
    """
    The function `cage_to_graph` takes a cage and a ringlist as input and returns a graph representation    of the cage.

    Args:
      cage: The `cage` parameter is a list of integers representing the rings in the cage. Each integer    corresponds to a ring in the `ringlist` parameter.
      ringlist: The `ringlist` parameter is a dictionary where the keys are ring numbers and the values    are lists of nodes that belong to each ring.

    Returns:
      The function `cage_to_graph` returns a graph object `g` created using the `nx.Graph()` function    from the NetworkX library.
    """
    g = nx.Graph()
    for ring in cage:
        nodes = ringlist[ring]
        nx.add_cycle(g, nodes)
        # for i in range(len(nodes)):
        #     g.add_edge(nodes[i-1], nodes[i])
    return g


def _reorder(cycle, first, second):
    """
    The function `_reorder` takes a cycle, a first element, and a second element as input, and returns a    reordered list of elements from the cycle based on the positions of the first and second elements.

    Args:
      cycle: The `cycle` parameter is a list representing a cycle of elements. Each element in the list    represents a node in the cycle, and the order of the elements in the list represents the order of    the nodes in the cycle.
      first: The `first` parameter is the element in the `cycle` list that you want to be the first    element in the reordered list.
      second: The "second" parameter in the given function is the element that should come immediately    after the "first" element in the reordered cycle.

    Returns:
      The function `_reorder` returns a list `r` that contains the elements of the `cycle` list in a    reordered manner. The order of the elements in `r` depends on the positions of `first` and `second`    in the `cycle` list.
    """
    s = cycle.index(first)
    if cycle[s - 1] == second:
        r = [cycle[i] for i in range(s, s - len(cycle), -1)]
    else:
        r = [cycle[i] for i in range(s - len(cycle), s)]
    return r


def _merge_cycles(cycle1, cycle2, first, second):
    """
    The function takes two cycles represented as lists of nodes and merges them into a larger cycle by    finding the common nodes and connecting them.

    Args:
      cycle1: A list of nodes representing the first cycle.
      cycle2: The `cycle2` parameter is a list of nodes representing a cycle.
      first: The `first` parameter is a list of nodes representing the first cycle.
      second: The `second` parameter is a list of nodes representing the second cycle.

    Returns:
      a large cycle, which is a combination of two smaller cycles. If the remaining parts of the cycle    have common nodes, the function returns None, indicating that the resulting cycle is not a simple    cycle.
    """
    logger = getLogger()
    r1 = _reorder(cycle1, first, second)
    r2 = _reorder(cycle2, first, second)
    logger.debug("#{0}+{1}".format(r1, r2))
    # zipper motion
    head = 0
    while r1[head - 1] == r2[head - 1]:
        head -= 1
        if head == -len(r1):
            return []
    tail = 1
    while r1[tail + 1 - len(r1)] == r2[tail + 1 - len(r2)]:
        tail += 1
    # unshared nodes of the cycles
    rest1 = set(r1) - set([r1[i] for i in range(head, tail + 1)])
    rest2 = set(r2) - set([r2[i] for i in range(head, tail + 1)])
    # if the remaining parts of the cycle have common nodes,
    if len(rest1 & rest2) != 0:
        # not a simple cycle
        return None
    cycle = [r1[i] for i in range(tail - len(r1), head)]
    cycle += [r2[i] for i in range(head, tail - len(r2), -1)]
    logger.debug(
        "#{0} {1} {2} {3} {4}".format(head, tail, cycle, rest1, rest2, rest1 & rest2)
    )
    return cycle


def _Triplets(cycle):
    tri = []
    for i in range(len(cycle)):
        tri.append((cycle[i - 2], cycle[i - 1], cycle[i]))
    return tri


def _Edges(cycle):
    ed = []
    for i in range(len(cycle)):
        ed.append((cycle[i - 1], cycle[i]))
    return ed


def polyhedra_iter(
    cycles: list, maxnfaces: int = 20, maxfragsize: int = 0, quick: bool = False
) -> list:
    """Quasi-polyhedra made of given cycles. A quasi-polyhedron is a polyhedron-like graph.

    Args:
        _cycles (list): List of cycles, typically made by cycless.cycles()
        maxnfaces (int, optional): maximum number of faces at a polyhedron. Defaults to 20.
        maxfragsize (int, optional): maximum number of nodes in a polyhedron. Defaults to 0 (not specified).
        quick (bool, optional): Avoid some tests for faster run.  Defaults to False.

    Returns:
        list: list of lists of cycle labels.
    """

    # Local functions

    def _register_triplets(cycle, cycleid):
        for triplet in _Triplets(cycle):
            _cyclesAtATriplet[triplet].append(cycleid)
            tr = tuple(reversed(triplet))
            _cyclesAtATriplet[tr].append(cycleid)

    def _register_edges(cycle, cycleid):
        for edge in _Edges(cycle):
            _cyclesAtAnEdge[edge].append(cycleid)
            ed = tuple(reversed(edge))
            _cyclesAtAnEdge[ed].append(cycleid)

    def _is_divided_by_the_polyhedron(poly, quick=False):
        if quick:
            return _is_divided_by_the_pokyhedron2(poly)
        nodes = set()
        for cycle in poly:
            nodes |= set(cycles[cycle])
        G2 = _G.copy()
        ebunch = []
        for i in nodes:
            for j in _G.neighbors(i):
                ebunch.append((i, j))
        # G2.remove_edges_from(ebunch)
        G2.remove_nodes_from(nodes)
        logger.debug(
            "NCOMPO: {0} {1}".format(nx.number_connected_components(G2), _ncompo)
        )
        return nx.number_connected_components(G2) > _ncompo

    def _is_divided_by_the_pokyhedron2(fragment):
        """fragmentに隣接する頂点で、その隣接点が全部fragmentの頂点であるようなものがあれば、そいつは孤立している。
        ただし、この考え方では、内部頂点が2つ以上あるような大フラグメントは見落す。
        """
        # fragmentに属する全ノード
        nodes = set()
        for cycle in fragment:
            nodes |= set(cycles[cycle])
        # fragmentに隣接する全ノードを抽出する
        adj = set()
        for node in nodes:
            for nei in _G[node]:
                if nei not in nodes:
                    adj.add(nei)
        # 隣接ノードの隣接が全部フラグメントに含まれているなら、そいつは孤立している
        for node in adj:
            linked = False
            for nei in _G[node]:
                if nei not in nodes:
                    linked = True
                    break
            if not linked:
                # logger.info("Isolated node")
                return True
        return False

    # Return True if the given fragment contains cycles that are not the
    # member of the fragment.
    def _contains_extra_cycles(fragment):
        tris = set()
        allnodes = set()
        # A fragment is a set of cycle IDs.
        for cycleid in fragment:
            nodes = cycles[cycleid]
            allnodes |= set(nodes)
            tris |= set(_Triplets(nodes))
        for tri in tris:
            for cycleid in _cyclesAtATriplet[tri]:
                if cycleid not in fragment:
                    # if all the nodes of a cycle is included in the fragment,
                    nodes = cycles[cycleid]
                    if len(set(nodes) - allnodes) == 0:
                        return True
                    # logger.debug(fragment,cycleid)
        return False

    # Grow up a set of cycles by adding new cycle on the perimeter.
    # Return the list of polyhedron.
    # origin is the cycle ID of the first face in the polyhedron

    def _progress(origin, peri, fragment, numCyclesOnTheNode):
        # Here we define a "face" as a cycle belonging to the (growing)
        # polyhedron.
        logger.debug(f"#{peri} {fragment}")
        if len(fragment) > maxnfaces:
            # logger.debug("#LIMITTER")
            return
        # if the perimeter closes,
        if len(peri) == 0:
            if _contains_extra_cycles(fragment):
                # If the fragment does not contain any extra cycle whose all
                # vertices belong to the fragment but the cycle is not a face,
                logger.debug("It contains extra cycles(s).")
            else:
                # If the polyhedron has internal vertices that are not a part of
                # the polyhedron (i.e. if the polyhedron does not divide the total
                # network into to components)
                if _is_divided_by_the_polyhedron(fragment, quick):
                    logger.info("It has internal vertices.")
                else:
                    # Add the fragment to the list.
                    # A fragment is a set of cycle IDs of the faces
                    fs = frozenset(fragment)
                    if fs not in _vitrites:
                        yield fragment
                        _vitrites.add(fs)
            # Search finished.
            return
        # If the perimeter is still open,
        for i in range(len(peri)):
            # If any vertex on the perimeter is shared by more than two faces,
            if numCyclesOnTheNode[peri[i]] > 2:
                logger.debug("#Failed(2)")
                return
        for i in range(len(peri)):
            # Look up the node on the perimeter which is shared by two faces.
            if numCyclesOnTheNode[peri[i]] == 2:
                # Reset the frag
                trynext = False
                # Three successive nodes around the node i
                center = peri[i]
                left = peri[i - 1]
                # Avoid to refer the out-of-list element
                right = peri[i + 1 - len(peri)]
                # Reset the frag
                success = False
                logger.debug(f"Next triplet:{left} {center} {right}")
                if (left, center, right) in _cyclesAtATriplet:
                    logger.debug(
                        "Here cycles are:{0}".format(
                            _cyclesAtATriplet[(left, center, right)]
                        )
                    )
                    for cycleid in _cyclesAtATriplet[(left, center, right)]:
                        logger.debug(f"#Next:{cycleid}")
                        # if the cycle is new and its ID is larger than the
                        # origin,
                        if origin < cycleid and cycleid not in fragment:
                            nodes = cycles[cycleid]
                            # Add the cycle as a face and extend the perimeter
                            newperi = _merge_cycles(peri, nodes, center, right)
                            logger.debug(f"#Result:{newperi}")
                            # result is not a simple cycle
                            if newperi is None:
                                trynext = True
                                logger.debug("#Try next!")
                            else:
                                for node in nodes:
                                    numCyclesOnTheNode[node] += 1
                                    mult = [numCyclesOnTheNode[i] for i in newperi]
                                    logger.debug(
                                        f"#{peri} {nodes} {edge} {newperi} {mult}"
                                    )
                                yield from _progress(
                                    origin,
                                    newperi,
                                    fragment
                                    | set(
                                        [
                                            cycleid,
                                        ]
                                    ),
                                    numCyclesOnTheNode,
                                )
                                for node in nodes:
                                    numCyclesOnTheNode[node] -= 1
                                # if result == True:
                                #    return True
                # it might be too aggressive
                if not trynext:
                    break
        logger.debug(f"#Failed to expand perimeter {peri} {fragment}")
        return

    logger = getLogger()

    if maxfragsize > 0:
        logger.warn("maxfragsize is deprecated. Use maxnfaces instead.")
        maxnfaces = maxfragsize
        del maxnfaces

    _cyclesAtATriplet = defaultdict(list)
    _cyclesAtAnEdge = defaultdict(list)

    for cycleid, cycle in enumerate(cycles):
        _register_triplets(cycle, cycleid)
        _register_edges(cycle, cycleid)
    # For counting the number of components separated by a polyhedral fragment
    _G = nx.Graph()

    for cycle in cycles:
        nx.add_cycle(_G, cycle)
    _ncompo = nx.number_connected_components(_G)

    _vitrites = set()
    # The first cycle
    for cycleid in range(len(cycles)):
        peri = cycles[cycleid]
        fragment = set([cycleid])
        edge = tuple(peri[0:2])
        numCyclesOnTheNode = defaultdict(int)
        # increment the number-of-cycles-at-a-node counter
        # for each node on the first cycle.
        for node in peri:
            numCyclesOnTheNode[node] = 1
            logger.debug("#Candid: {0} {1}".format(cycleid, _cyclesAtAnEdge[edge]))
        # The second cycle, which is adjacent to the first one.
        for cycleid2 in _cyclesAtAnEdge[edge]:
            # The second one must have larger cycle ID than the first one.
            if cycleid < cycleid2:
                nodes = cycles[cycleid2]
                # Make the perimeter of two cycles.
                newperi = _merge_cycles(peri, nodes, edge[0], edge[1])
                if newperi is not None:
                    # increment the number-of-cycles-at-a-node counter
                    # for each node on the second cycle.
                    for node in nodes:
                        numCyclesOnTheNode[node] += 1
                        mult = [numCyclesOnTheNode[i] for i in newperi]
                        logger.debug(
                            "{0} {1} {2} {3} {4}".format(
                                peri, nodes, edge, newperi, mult
                            )
                        )
                    # Expand the perimeter by adding new faces to the
                    # polyhedron.
                    yield from _progress(
                        cycleid, newperi, set([cycleid, cycleid2]), numCyclesOnTheNode
                    )
                    # decrement the number-of-cycles-at-a-node counter
                    # for each node on the second cycle.
                    for node in nodes:
                        numCyclesOnTheNode[node] -= 1
    return _vitrites


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
    A = [cycle for cycle in cycles_iter(g, 4, pos=coord)]
    print(f"Number of cycles (PBC compliant): {len(A)}")
    assert len(A) == 192

    vitrites = [v for v in polyhedra_iter(A)]
    print(f"Number of cubes: {len(vitrites)}")
    assert len(vitrites) == 64


if __name__ == "__main__":
    test()
