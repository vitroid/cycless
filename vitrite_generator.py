#!/usr/bin/env python
# coding: utf-8
import graph_database as gdb
import distance_matrix as dm

# Generate all possible 3-regular planar graphs
# Starting from tetrahedral graph.
# It means, #8 is not included in this family of graphs.

# 有限サイズの全探索をするためには、辺の除去も必要じゃないかな。
# 8番のような構造をそもそも表現する方法が思いつかない。
# そしてそのタイプのグラフがリングの数えあげを困難にしている。

import itertools as it


def subdivide(edges, faces, size, db, graph_list):
    # print "SUBDIVIDE",edges,faces
    # consistency check
    if True:
        ok = True
        tmp = dict()
        for f in faces:
            for k in range(len(f)):
                key = frozenset([f[k - 1], f[k]])
                if key not in tmp:
                    tmp[key] = 0
                tmp[key] += 1
        for e in edges:
            if tmp[e] != 2:
                print "ERR-", e, tmp[e]
                ok = False
        for e in tmp:
            if e not in edges:
                print "ERR+", e
                ok = False
        if not ok:
            import sys
            sys.exit(1)
    for face in faces:
        for ei, ej in it.combinations(range(len(face)), 2):
            # always ei<ej
            vi = size
            vj = size + 1
            ei0 = ei
            ei1 = (ei + 1) % len(face)
            ej0 = ej
            ej1 = (ej + 1) % len(face)
            # modifications to the edges
            newedges = edges.copy()
            # print newedges
            newedges.remove(frozenset([face[ei0], face[ei1]]))
            newedges.remove(frozenset([face[ej0], face[ej1]]))
            newedges.add(frozenset([face[ei0], vi]))
            newedges.add(frozenset([face[ei1], vi]))
            newedges.add(frozenset([face[ej0], vj]))
            newedges.add(frozenset([face[ej1], vj]))
            newedges.add(frozenset([vi, vj]))
            # print edges
            # print newedges
            # print
            # modifications to the faces
            face0 = face[0:ei1] + [vi, vj] + face[ej0 + 1:size]
            face1 = face[ei1:ej0 + 1] + [vj, vi]
            if len(face1) == 2:
                print face, ei, ej
                sys.exit(1)
            tmp = list(faces)
            tmp.remove(face)
            # print tmp
            newfaces = []
            for f in tmp:
                fp = f + [f[0]]
                # print fp,(ei1,ei0),(ej1,ej0)
                e = []
                for k in range(len(f)):
                    a, b = fp[k:k + 2]
                    e.append(a)
                    if (a, b) == (face[ei1], face[ei0]):
                        e.append(vi)
                    elif (a, b) == (face[ej1], face[ej0]):
                        e.append(vj)
                newfaces.append(e)
            newfaces += [face0, face1]
            # print faces
            # print newfaces
            # print

            # These conditions are too strict.
            # You may miss the dodecahedron with this procedure.
            if 8 < len(face0) or 8 < len(face1):
                # reject if the graph contains huge rings
                continue
            if 12 < len(newfaces):
                # reject if the graph has too many faces
                continue
            newgraph = dm.adjacency_table(newedges, size + 2)
            lastlen = len(graph_list)
            id = gdb.graph_query(newgraph, db, graph_list, add=True)
            if lastlen < len(graph_list):
                print "new", id  # ,newgraph
                # print faces
                # print newfaces
                subdivide(newedges, newfaces, size + 2, db, graph_list)
            else:
                print "found", id


# tetrahedral graph; minimal simple 3-regular planar graph
_e = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
edges = set([frozenset(j) for j in _e])
# clockwise
faces = [[0, 1, 2], [0, 2, 3], [0, 3, 1], [3, 2, 1]]
size = 4
graph = dm.adjacency_table(edges, size)

print graph

db = dict()
graph_list = []
id = gdb.graph_query(graph, db, graph_list, add=True)
print id

subdivide(edges, faces, size, db, graph_list)
