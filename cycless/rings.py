#!/usr/bin/env python3

from typing import Generator

import numpy as np
import networkx as nx
import click
from dataclasses import dataclass
from functools import cache

from cycless.cycles import cycles_iter


# for ring, which is a cycle graph with edge orientations.


# for pDoc3
__all__ = ["dicycles_iter"]


@dataclass
class Ring:
    """基底無向グラフがサイクルである有向グラフをRingと定義する。"""

    # 頂点の並び
    path: tuple
    # 辺の向き
    ori: tuple
    # 辺の向きのパターンを表すラベル
    code: int


@cache
def isomorphs(ori: tuple):
    """
    return the symmetric alternatives of cycle a
    """
    iso = set()
    aa = ori + ori
    for i in range(len(ori)):
        part = tuple(aa[i : i + len(ori)])
        iso.add(part)
    e = [not x for x in ori]
    ee = e + e
    for i in range(len(ori)):
        part = tuple(ee[i : i + len(ori)])
        iso.add(part)
    return iso


@cache
def code(ori: tuple):
    """
    from an array of True/False to an integer.
    """
    s = 0
    for i in range(len(ori)):
        if ori[i]:
            s += 1 << i
    return s


@cache
def encode(ori: tuple):
    m = 9999
    for i in isomorphs(ori):
        c = code(i)
        if c < m:
            m = c
    return m


@cache
def symmetry(ori: tuple):
    """
    return the symmetry number of cycle a
    """
    return len(isomorphs(ori))


def cycle_orientations_iter(
    digraph: nx.DiGraph, maxsize: int, pos: np.ndarray = None
) -> Generator[tuple, None, None]:
    """有向グラフを無向グラフとみなしてサイクルをさがし、サイクルとその上の有向辺の向きを返す。

    Args:
        digraph (nx.DiGraph): 有向グラフ
        maxsize (int): サイクルの最大サイズ
        pos (np.ndarray, optional): 頂点のセル相対座標。これが与えられた場合は、
            周期境界を跨がないサイクルだけを調査する. Defaults to None.

    Yields:
        Generator[tuple, None, None]: _description_
    """

    def orientations(path: tuple, digraph: nx.DiGraph) -> list:
        """与えられたパスまたはサイクルの向きの有向辺があるかどうかを、boolのリストで返す

        Args:
            path (Iterable): 頂点ラベルのリスト
            digraph (nx.DiGraph): もとの有向グラフ

        Returns:
            list: 辺の向き
        """
        ori = tuple([digraph.has_edge(path[i - 1], path[i]) for i in range(len(path))])
        ori_code = encode(ori)
        return Ring(path=path, ori=ori, code=ori_code)

    for cycle in cycles_iter(nx.Graph(digraph), maxsize, pos):
        yield orientations(cycle, digraph)


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

    # rings
    D = [ring for ring in cycle_orientations_iter(dg, 4)]
    logger.debug(f"Number of cycles (crude)        : {len(D)}")
    logger.debug(D)
    assert len(D) == 240
    logger.info("Test 4 Pass")


if __name__ == "__main__":
    test()
