# -*- coding: utf-8 -*-
"""
.. include:: ../README.md
"""

import numpy as np
import networkx as nx


def center_of_graph(g: nx.Graph, node_frac: np.ndarray) -> np.ndarray:
    # 辺をたどりながらグラフの中心を計算する。
    first_node = next(iter(g.nodes()))
    positions = {first_node: node_frac[first_node]}

    def dfs(node):
        for nei in g.neighbors(node):
            origin = positions[node]
            if nei not in positions:
                delta = node_frac[nei] - origin
                delta -= np.floor(delta + 0.5)
                positions[nei] = origin + delta
                dfs(nei)

    dfs(first_node)
    return np.mean(list(positions.values()), axis=0)
