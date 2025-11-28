#!/usr/bin/env python3

from typing import Generator

import numpy as np
import networkx as nx
import click


# for a directed graph


# for pDoc3
__all__ = ["dicycles_iter"]


def dicycles_iter(
    digraph: nx.DiGraph, size: int, vec: bool = False
) -> Generator[tuple, None, None]:
    """
    The `dicycles_iter` function is used to find homodromic cycles of a specified size in a given
    directed graph.

    Args:
      digraph (nx.DiGraph): a directed graph. It can be represented as a data structure such as a dictionary of dictionaries or a networkx DiGraph object. It contains information about the connections between nodes in the graph.
      size (int): the desired length of the cycles that you want to find in the given digraph.
      vec (bool): a boolean flag that determines whether the orientations of the vectors are given as attributes of the edges. If `vec` is set to True, the function will check the dipole moment of each cycle to determine if it is a homodromic cycle. Defaults to False
    """

    # """Homodromic cycles in a given digraph.

    # Args:
    #     digraph (nx.DiGraph): the digraph.
    #     size (int): size of a cycle. (only one size)
    #     vec (bool, optional): If True, the orientations of the vectors is given as the attributes of the edges and the spanning cycles are avoided. Defaults to False.

    # Yields:
    #     Generator[tuple, None, None]: List of lists of node labels.
    # """

    def _find(digraph, history, size):
        """
        The `_find` function recursively searches for all cycles of a specified size in a directed graph and
        returns them as tuples.

        Args:
          digraph: a directed graph. It can be represented as a
        dictionary of dictionaries or a networkx DiGraph object. It contains information about the
        connections between nodes in the graph.
          history: a list that tracks the nodes that have
        been accessed so far in a depth-first search algorithm. It starts as an empty list and gets updated
        as the algorithm progresses through the graph.
          size: the required length of the path or
        cycle that you are trying to search for within the directed graph. It specifies the number of nodes
        that should be included in the cycle that is being searched for recursively.
        """
        head = history[0]
        last = history[-1]
        if len(history) == size:
            for succ in digraph.successors(last):
                if succ == head:
                    # test the dipole moment of a cycle.
                    if vec:
                        d = 0.0
                        for i in range(len(history)):
                            a, b = history[i - 1], history[i]
                            d = d + digraph[a][b]["vec"]
                        if np.allclose(d, np.zeros_like(d)):
                            yield tuple(history)
                    else:
                        yield tuple(history)
        else:
            for succ in digraph.successors(last):
                if succ < head:
                    # Skip it;
                    # members must be greater than the head
                    continue
                if succ not in history:
                    # recurse
                    yield from _find(digraph, history + [succ], size)

    for head in digraph.nodes():
        yield from _find(digraph, [head], size)


@click.command()
@click.option("-d", "--debug", is_flag=True)
def test(debug):
    """
    「test」関数は格子グラフを生成し、グラフ内の周期境界条件 (PBC) に準拠しているサイクル数と準拠していないサイクル数を計算します。
    """
    import random
    from logging import getLogger, basicConfig, INFO, DEBUG

    if debug:
        basicConfig(level=DEBUG)
    else:
        basicConfig(level=INFO)
    logger = getLogger()

    logger.info("Self-test mode")
    random.seed(1)
    dg = nx.DiGraph()
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
                # orient randomly
                if random.randint(0, 1) == 0:
                    dg.add_edge(a, b, vec=d)
                else:
                    dg.add_edge(b, a, vec=-d)
    # PBC-compliant
    A = set([cycle for cycle in dicycles_iter(dg, 4, vec=True)])
    logger.debug(f"Number of cycles (PBC compliant): {len(A)}")
    logger.debug(A)
    assert len(A) == 25
    logger.info("Test 1 Pass")

    # not PBC-compliant
    B = set([cycle for cycle in dicycles_iter(dg, 4)])
    logger.debug(f"Number of cycles (crude)        : {len(B)}")
    logger.debug(B)
    assert len(B) == 33
    logger.info("Test 2 Pass")

    # difference
    C = B - A
    logger.debug("Cycles that span the cell:")
    logger.debug(C)
    assert len(C) == 8
    logger.info("Test 3 Pass")


if __name__ == "__main__":
    test()
