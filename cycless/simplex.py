import networkx as nx
from typing import Generator, Union


__all__ = ["triangles_iter", "tetrahedra_iter", "octahedra_iter", "tetra_adjacency"]


def triangles_iter(g: Union[dict, nx.Graph]) -> Generator[tuple, None, None]:
    """
    The `triangles_iter` function generates all triangles in a given graph by iterating over all
    vertices and their adjacent vertices.

    Args:
      g (Union[dict, nx.Graph]): Represents a graph where each vertex is a key in the     dictionary `g`, and the corresponding value is a set of vertices that are adjacent to the key     vertex.
    """
    # gに含まれるすべて頂点iに関して
    for i in g:
        # iに隣接するすべての頂点jに関して
        for j in g[i]:
            # 同じサイクルを二度数えないように、j>iに限定
            if j > i:
                # jに隣接するすべての頂点kに関して
                for k in g[j]:
                    if k > j:
                        # もしiがkに隣接しているなら
                        if i in g[k]:
                            yield i, j, k


def tetrahedra_iter(g: nx.Graph) -> Generator[tuple, None, None]:
    """
    The function `tetrahedra_iter` generates all possible tetrahedra in a given graph.

    Args:
      g (nx.Graph): The parameter `g` is a graph represented as an instance of the `nx.Graph` class from
    the NetworkX library.
    """
    for i, j, k in triangles_iter(g):
        for l in g[k]:
            if l > k:
                if l in g[j]:
                    if i in g[l]:
                        yield i, j, k, l


# 探索したいグラフを定義する。
template = nx.Graph(
    [
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 1),
        (1, 5),
        (2, 5),
        (3, 5),
        (4, 5),
    ]
)


def octahedra_iter(g: nx.Graph) -> Generator[list, None, None]:
    """
    The function `octahedra_iter` is a generator that yields lists of node labels that form octahedral
    subgraphs in a given graph.

    Args:
      g (nx.Graph): The parameter `g` is a networkx graph. It represents the input graph on which we    want to find octahedral subgraphs.
    """
    ismags = nx.isomorphism.ISMAGS(g, template)
    # symmetry=Trueにしておくと、同じ四面体に1回だけマッチする(24回ではない)。
    for hctam in ismags.subgraph_isomorphisms_iter(symmetry=True):
        # 辞書のkeyとvalueを交換する。
        match = {b: a for a, b in hctam.items()}
        # 0と5、1と3、2と4の間に辺があったら、それは八面体と言えない。
        # そういうものは、双四角錐と呼ぶべき。
        if match[0] in g[match[5]]:
            continue
        if match[1] in g[match[3]]:
            continue
        if match[2] in g[match[4]]:
            continue
        yield list(hctam.keys())


def tetra_adjacency(g: nx.Graph) -> tuple:
    """
    The function `tetra_adjacency` takes a graph as input, extracts the tetrahedra from the graph,
    assigns unique IDs to each tetrahedron, and creates an adjacency graph of the tetrahedra.

    Args:
      g (nx.Graph): The parameter `g` is a networkx Graph object that represents the adjacency    relationships between atoms.

    Returns:
      a tuple containing two elements:
    1. `tet_memb`: a list of tetrahedra specified by the labels of the nodes.
    2. `gtet`: an adjacency graph of the tetrahedra.
    """

    tet_memb = [ijkl for ijkl in tetrahedra_iter(g)]

    # あとで扱いやすいように、四面体に通し番号を付ける
    tet_id = {memb: id for id, memb in enumerate(tet_memb)}

    # 四面体の隣接グラフを作る
    triangles = dict()
    gtet = nx.Graph()
    for ijkl in tet_memb:
        i, j, k, l = ijkl
        for tri in [(i, j, k), (i, j, l), (i, k, l), (j, k, l)]:
            if tri in triangles:
                nei = triangles[tri]
                gtet.add_edge(tet_id[ijkl], tet_id[nei])
            triangles[tri] = ijkl

    return tet_memb, gtet
