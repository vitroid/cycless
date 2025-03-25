from logging import getLogger
from methodtools import lru_cache
import itertools
from typing import Generator, Optional, Any, Set, List, Tuple, FrozenSet
import heapq
from functools import wraps
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

import numpy as np
import networkx as nx

# for pDoc3
__all__ = ["cycles_iter"]


def centerOfMass(members, rpos):
    origin = rpos[list(members)[0]]
    d = rpos[list(members)] - origin
    d -= np.floor(d + 0.5)
    relcom = np.mean(d, axis=0)
    com = origin + relcom
    com -= np.floor(com)
    return com


class CycleFinder:
    def __init__(self, graph: nx.Graph, pos: Optional[np.ndarray] = None):
        self.graph = graph
        self.pos = pos
        self._pathlen_cache = {}

    def _is_spanning(self, cycle):
        """
        The function `_is_spanning` checks if a given cycle spans the periodic cell in a simulation.

        Args:
          cycle: It seems like the `cycle` parameter is a list of indices representing a cycle in a graph or
        a sequence. The function `_is_spanning` is checking whether this cycle spans the periodic cell based
        on the positions stored in the `pos` variable.

        Returns:
          a boolean value - True if the cycle spans the periodic cell, and False otherwise.
        """
        total = np.zeros_like(self.pos[cycle[0]])
        N = len(cycle)
        for i, j in zip(cycle[-1:] + cycle[:-1], cycle):
            d = self.pos[i] - self.pos[j]
            d -= np.floor(d + 0.5)
            total += d
        return np.any(np.absolute(total) > 1e-5)

    def _shortest_pathlen(self, pair):
        if pair not in self._pathlen_cache:
            self._pathlen_cache[pair] = len(nx.shortest_path(self.graph, *pair)) - 1
        return self._pathlen_cache[pair]

    def _shortcuts(self, members):
        n = len(members)
        for i in range(0, n):
            for j in range(i + 1, n):
                d = min(j - i, n - (j - i))
                if d > self._shortest_pathlen(frozenset((members[i], members[j]))):
                    return True
        return False

    def _complete_cycle(
        self, x: int, y: int, z: int
    ) -> Generator[List[int], None, None]:
        """
        Generates complete cycles starting from node x, passing through nodes y and z.

        This method finds all possible cycles that:
        1. Start at node x
        2. Pass through nodes y and z in that order
        3. Return to the starting node x
        4. Do not contain any shortcuts (i.e., are minimal cycles)

        Args:
            x (int): The starting node of the cycle
            y (int): The first intermediate node
            z (int): The second intermediate node

        Yields:
            List[int]: A list of nodes forming a complete cycle, where:
                - The first element is x
                - The last element is y
                - The cycle is minimal (contains no shortcuts)

        Example:
            >>> finder = CycleFinder(graph)
            >>> for cycle in finder._complete_cycle(0, 1, 2):
            ...     print(cycle)
            [0, 2, 3, 1]  # Example output
        """
        for cycle in self._shortest_paths(z, y, {x}):
            members = [x] + cycle
            assert cycle[0] == z and cycle[-1] == y
            if not self._shortcuts(members):
                yield members

    def _shortest_paths(self, start, end, exclude=set()):
        """改良版shortest_paths関数"""
        visited = {start: [[start]]}  # ノードに対する全パスを保持
        queue = [(0, start)]
        min_cost = float("inf")

        while queue:
            cost, current = heapq.heappop(queue)

            if cost > min_cost:
                break

            if current == end:
                min_cost = cost
                for path in visited[current]:
                    yield path
                continue

            for neighbor in self.graph[current]:
                if neighbor in exclude:
                    continue

                new_cost = cost + 1
                if new_cost < min_cost:
                    if neighbor not in visited:
                        visited[neighbor] = []
                        heapq.heappush(queue, (new_cost, neighbor))
                    for path in visited[current]:
                        if neighbor not in path:
                            visited[neighbor].append(
                                path + [neighbor]
                            )  # shortest_pathsの実装

    # def _shortest_paths(self, start, end, exclude=set(), maxedges=999999):
    #     """
    #     The function `shortest_paths` finds all shortest paths from a start node to an end node in a graph,
    #     excluding specified nodes and limiting the maximum number of edges.

    #     Args:
    #       G: The parameter `G` in the `shortest_paths` function is expected to be a graph represented as a
    #     dictionary where the keys are nodes and the values are lists of neighboring nodes. This dictionary
    #     represents the connections between nodes in the graph.
    #       start: The `start` parameter in the `shortest_paths` function represents the starting node from
    #     which you want to find the shortest paths in the graph `G`. It is the node where the path search
    #     begins.
    #       end: The `end` parameter in the `shortest_paths` function represents the destination node in the
    #     graph `G` to which you want to find the shortest paths from the `start` node.
    #       exclude: The `exclude` parameter in the `shortest_paths` function is a set that contains nodes
    #     which should be excluded from the path finding process. If a node is in the `exclude` set, it will
    #     not be visited during the path traversal. This can be useful when you want to avoid certain
    #       maxedges: The `maxedges` parameter in the `shortest_paths` function represents the maximum number
    #     of edges allowed in a path. This parameter is used to limit the search space and prevent the
    #     algorithm from exploring paths that are longer than the specified maximum number of edges. If a path
    #     exceeds the `maxedges. Defaults to 999999
    #     """
    #     q = [
    #         (
    #             0,
    #             [
    #                 start,
    #             ],
    #         )
    #     ]  # Heap of (cost, path)
    #     cheapest = maxedges
    #     while len(q):
    #         # logger.debug(q)
    #         (cost, path) = heapq.heappop(q)
    #         if cost > cheapest:
    #             break
    #         v0 = path[-1]
    #         if v0 == end:
    #             cheapest = cost  # first arrived
    #             yield path
    #         else:
    #             if v0 in exclude:
    #                 continue
    #             # exclude.add(v0)
    #             for v1 in self.graph[v0]:
    #                 if v1 not in exclude:
    #                     heapq.heappush(q, (cost + 1, path + [v1]))

    def find_cycles(self, maxsize: Optional[int] = None):
        """
        Finds all cycles in the graph up to a specified maximum size.

        Args:
            maxsize (Optional[int]): The maximum size of cycles to find. If None, all cycles will be found.

        Yields:
            Tuple[int, ...]: A tuple of node indices forming a cycle.
        """
        rings = set()
        for x in self.graph:
            neis = sorted(self.graph[x])
            for y, z in itertools.combinations(neis, 2):
                for cycle in self._complete_cycle(x, y, z):
                    if maxsize is not None and len(cycle) > maxsize:
                        continue
                    j = frozenset(cycle)
                    if j not in rings:
                        if self.pos is None or not self._is_spanning(cycle):
                            yield tuple(cycle)
                            rings.add(j)


@dataclass
class CyclesInputValidator:
    """cycles_iterの入力検証クラス"""

    graph: nx.Graph
    maxsize: Optional[int] = None
    pos: Optional[np.ndarray] = None

    def __post_init__(self):
        """入力値の検証"""
        self._validate_graph()
        self._validate_maxsize()
        self._validate_pos()

    def _validate_graph(self):
        if not isinstance(self.graph, nx.Graph):
            raise TypeError("graph must be a NetworkX Graph")

    def _validate_maxsize(self):
        if self.maxsize is not None and self.maxsize < 3:
            raise ValueError("maxsize must be at least 3")

    def _validate_pos(self):
        if self.pos is not None:
            if not isinstance(self.pos, np.ndarray):
                raise TypeError("pos must be a numpy array")
            if len(self.pos) != len(self.graph):
                raise ValueError("pos must have same length as number of nodes")


def validate_cycles_input(func):
    """拡張された検証デコレータ"""

    @wraps(func)
    def wrapper(
        graph: nx.Graph, maxsize: Optional[int] = None, pos: Optional[np.ndarray] = None
    ) -> Any:
        validator = CyclesInputValidator(graph, maxsize, pos)
        return func(graph, maxsize, pos)

    return wrapper


@validate_cycles_input
def cycles_iter(
    graph: nx.Graph, maxsize: Optional[int] = None, pos: Optional[np.ndarray] = None
) -> Generator[Tuple[int, ...], None, None]:
    """
    The function `cycles_iter` is a generator that finds all cycles in an undirected graph up to a
    specified maximum size, and optionally checks if the cycles span a periodic cell based on fractional
    coordinates of the nodes.

    Args:
      graph (nx.Graph): The `graph` parameter is an undirected graph represented using the `nx.Graph`
      class from the NetworkX library. It represents the connections between nodes in the graph.
      maxsize (Optional[int]): The maximum size of cycles to find. If None, all cycles will be found.
      pos (np.ndarray): The `pos` parameter is an optional argument that represents the fractional
      coordinates of the nodes in the graph. It is a numpy array of shape (n, m), where n is the number of
      nodes in the graph. Each row in the array represents the fractional coordinates of a node in the
      graph.

    Yields:
      Tuple[int, ...]: A tuple of node indices forming a cycle.
    """
    finder = CycleFinder(graph, pos)
    yield from finder.find_cycles(maxsize)


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
    assert len(A) == 192

    # not PBC-compliant
    B = set([cycle for cycle in cycles_iter(g, 4)])
    print(f"Number of cycles (crude)        : {len(B)}")
    print(B)
    assert len(B) == 240

    # difference
    C = B - A
    print("Cycles that span the cell:")
    print(C)
    assert len(C) == 48

    # g1 = nx.Graph([(1,2),(2,3),(3,4)])
    # g2 = nx.Graph([(1,4)])
    # print(graph_overlap(g1,g2))


def test_performance():
    """計算時間のオーダーを確認するテスト"""
    import time
    from statistics import mean, stdev

    # テスト用のグラフサイズ
    sizes = [4, 6, 8, 10]  # 4x4x4, 6x6x6, 8x8x8, 10x10x10
    results = []

    print("\n計算時間のオーダー確認:")
    print("-" * 50)
    print("サイズ\tノード数\t辺の数\t\t計算時間(秒)\tサイクル数")
    print("-" * 50)

    for size in sizes:
        # グラフ生成
        g = nx.Graph()
        X, Y, Z = np.meshgrid(np.arange(size), np.arange(size), np.arange(size))
        X = X.reshape(size**3)
        Y = Y.reshape(size**3)
        Z = Z.reshape(size**3)
        coord = np.array([X, Y, Z]).T * 1.0 / size

        # import pairlist as pl

        # for a, b, d in pl.pairs_iter(coord, 1.1, np.eye(3) * size):
        #     g.add_edge(a, b)
        # 辺の追加

        for a in range(size**3):
            for b in range(a):
                d = coord[b] - coord[a]
                d -= np.floor(d + 0.5)
                if d @ d < (1 / (size - 1)) ** 2:
                    g.add_edge(a, b)

        # 計算時間の計測（5回実行）
        times = []
        cycles = None
        for i in range(5):
            start_time = time.time()
            cycles = list(cycles_iter(g, maxsize=4, pos=coord))
            end_time = time.time()
            times.append(end_time - start_time)

        # 結果の記録
        results.append(
            {
                "size": size,
                "nodes": len(g),
                "edges": len(g.edges),
                "time": mean(times),
                "time_std": stdev(times),
                "cycles": len(cycles),
            }
        )

        # 結果の表示
        print(
            f"{size}x{size}x{size}\t{len(g)}\t\t{len(g.edges)}\t\t{mean(times):.3f}±{stdev(times):.3f}\t{len(cycles)}"
        )

    # オーダーの分析
    print("\nオーダー分析:")
    print("-" * 50)
    for i in range(len(results) - 1):
        size_ratio = results[i + 1]["size"] / results[i]["size"]
        time_ratio = results[i + 1]["time"] / results[i]["time"]
        node_ratio = results[i + 1]["nodes"] / results[i]["nodes"]
        edge_ratio = results[i + 1]["edges"] / results[i]["edges"]
        cycle_ratio = results[i + 1]["cycles"] / results[i]["cycles"]

        print(f"\n{results[i]['size']} → {results[i+1]['size']}:")
        print(f"  時間比: {time_ratio:.2f}x")
        print(f"  ノード比: {node_ratio:.2f}x")
        print(f"  辺の比: {edge_ratio:.2f}x")
        print(f"  サイクル数比: {cycle_ratio:.2f}x")


if __name__ == "__main__":
    test()
    test_performance()
