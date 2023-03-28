import networkx as nx

def triangles_iter(g):
    """Generator of triangle subgraphs

    Args:
        g (networkx.Graph): a graph.

    Yields:
        list of int: labels of the nodes
    """
    # gに含まれるすべて頂点iに関して
    for i in g:
        # iに隣接するすべての頂点jに関して
        for j in g[i]:
            # 同じサイクルを二度数えないように、j>iに限定
            if j>i:
                # jに隣接するすべての頂点kに関して
                for k in g[j]:
                    if k>j:
                        #もしiがkに隣接しているなら
                        if i in g[k]:
                            yield i,j,k


def tetrahedra_iter(g):
    """Generator of tetrahedral subgraphs

    Args:
        g (networkx.Graph):  a graph.

    Yields:
        list of int: labels of the nodes
    """
    for i,j,k in triangles_iter(g):
        for l in g[k]:
            if l>k:
                if l in g[j]:
                    if i in g[l]:
                        yield i,j,k,l



# 探索したいグラフを定義する。
template = nx.Graph([(0,1),(0,2),(0,3),(0,4),
                (1,2),(2,3),(3,4),(4,1),
                (1,5),(2,5),(3,5),(4,5)])

def octahedra_iter(g):
    """Generator of octahedral subgraphs

    Args:
        g (networkx.Graph):  a graph.

    Yields:
        list of int: labels of the nodes matched to the template
    """
    ismags = nx.isomorphism.ISMAGS(g, template)
    # symmetry=Trueにしておくと、同じ四面体に1回だけマッチする(24回ではない)。
    for hctam in ismags.subgraph_isomorphisms_iter(symmetry=True):
        # 辞書のkeyとvalueを交換する。
        match = {b:a for a,b in hctam.items()}
        # 0と5、1と3、2と4の間に辺があったら、それは八面体と言えない。
        # そういうものは、双四角錐と呼ぶべき。
        if match[0] in g[match[5]]:
            continue
        if match[1] in g[match[3]]:
            continue
        if match[2] in g[match[4]]:
            continue
        yield list(hctam.keys())


def tetra_adjacency(g):
    """グラフから四面体を抽出し、さらにその隣接関係をグラフにして返す。

    Args:
        g (networx.Graph): 原子の隣接関係

    Returns:
        list of tetrahedra, specified by the labels of the nodes
        adjacency graph of the tetrahedra
    """

    tet_memb = [ijkl for ijkl in tetrahedra_iter(g)]

    # あとで扱いやすいように、四面体に通し番号を付ける
    tet_id = {memb:id for id, memb in enumerate(tet_memb)}

    # 四面体の隣接グラフを作る
    triangles = dict()
    gtet = nx.Graph()
    for ijkl in tet_memb:
        i,j,k,l = ijkl
        for tri in [(i,j,k), (i,j,l), (i,k,l), (j,k,l)]:
            if tri in triangles:
                nei = triangles[tri]
                gtet.add_edge(tet_id[ijkl], tet_id[nei])
            triangles[tri] = ijkl

    return tet_memb, gtet
