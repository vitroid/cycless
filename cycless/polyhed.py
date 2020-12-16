#!/usr/bin/env python3
#
# Simplified from github/Vitrite

import sys
import networkx as nx
from logging import getLogger
from collections import defaultdict
import numpy as np

from cycless.cycles import cycles_iter

def cage_to_graph(cage, ringlist):
    "Convert a cage as a set of cycles to a graph. "
    g = nx.Graph()
    for ring in cage:
        nodes = ringlist[ring]
        for i in range(len(nodes)):
            g.add_edge(nodes[i-1], nodes[i])
    return g



def _reorder(cycle,first,second):
    "Reorder the cycle noders so as to start from the first node."
    s = cycle.index(first)
    if cycle[s-1] == second:
        r = [cycle[i] for i in range(s,s-len(cycle),-1)]
    else:
        r = [cycle[i] for i in range(s-len(cycle),s)]
    return r


def _MergeCycles(cycle1,cycle2,first,second):
    "get two lists of nodes (cycles) and make a large cycle."
    logger = getLogger()
    r1 = _reorder(cycle1,first,second)
    r2 = _reorder(cycle2,first,second)
    logger.debug("#{0}+{1}".format(r1,r2))
    #zipper motion
    head=0
    while r1[head-1] == r2[head-1]:
        head -= 1
        if head == -len(r1):
            return []
    tail=1
    while r1[tail+1-len(r1)] == r2[tail+1-len(r2)]:
        tail += 1
    #unshared nodes of the cycles
    rest1 = set(r1) - set([r1[i] for i in range(head,tail+1)])
    rest2 = set(r2) - set([r2[i] for i in range(head,tail+1)])
    #if the remaining parts of the cycle have common nodes,
    if len(rest1 & rest2) != 0:
        #not a simple cycle
        return None
    cycle = [r1[i] for i in range(tail-len(r1),head)]
    cycle += [r2[i] for i in range(head,tail-len(r2),-1)]
    logger.debug("#{0} {1} {2} {3} {4}".format(head,tail,cycle,rest1,rest2,rest1 & rest2))
    return cycle


def _Triplets(cycle):
    tri = []
    for i in range(len(cycle)):
        tri.append((cycle[i-2],cycle[i-1],cycle[i]))
    return tri


def _Edges(cycle):
    ed = []
    for i in range(len(cycle)):
        ed.append((cycle[i-1],cycle[i]))
    return ed


def polyhedra_iter(_cycles, maxnfaces=20, maxfragsize=0):
    """
    A generator of polyhedra (combinations of cycles)

    maxnfaces: Maximum number of faces.
    maxfragsize: same as maxnfaces (deprecated)
    """
    #Local functions

    def _RegisterTriplets(cycle,cycleid):
        for triplet in _Triplets(cycle):
            _cyclesAtATriplet[triplet].append(cycleid)
            tr = tuple(reversed(triplet))
            _cyclesAtATriplet[tr].append(cycleid)

    def _RegisterEdges(cycle,cycleid):
        for edge in _Edges(cycle):
            _cyclesAtAnEdge[edge].append(cycleid)
            ed = tuple(reversed(edge))
            _cyclesAtAnEdge[ed].append(cycleid)

    def _IsDivided(fragment):
        nodes = set()
        for cycle in fragment:
            nodes |= set(_cycles[cycle])
        G2 = _G.copy()
        ebunch = []
        for i in nodes:
            for j in _G.neighbors(i):
                ebunch.append((i,j))
        #G2.remove_edges_from(ebunch)
        G2.remove_nodes_from(nodes)
        logger.debug("NCOMPO: {0} {1}".format(nx.number_connected_components(G2),_ncompo))
        return nx.number_connected_components(G2) > _ncompo

    #Return True if the given fragment contains cycles that are not the member of the fragment.
    def _ContainsExtraCycle(fragment):
        tris = set()
        allnodes = set()
        #A fragment is a set of cycle IDs.
        for cycleid in fragment:
            nodes = _cycles[cycleid]
            allnodes |= set(nodes)
            tris |= set(_Triplets(nodes))
        for tri in tris:
            for cycleid in _cyclesAtATriplet[tri]:
                if cycleid not in fragment:
                    #if all the nodes of a cycle is included in the fragment,
                    nodes = _cycles[cycleid]
                    if len(set(nodes) - allnodes) == 0:
                        return True
                    #logger.debug(fragment,cycleid)
        return False
    #Grow up a set of cycles by adding new cycle on the perimeter.
    #Return the list of polyhedron.
    #origin is the cycle ID of the first face in the polyhedron
    def _Progress(origin, peri, fragment, numCyclesOnTheNode):
        #Here we define a "face" as a cycle belonging to the (growing) polyhedron.
        logger.debug(f"#{peri} {fragment}")
        if len(fragment) > maxnfaces:
            #logger.debug("#LIMITTER")
            return
        #if the perimeter closes,
        if len(peri) == 0:
            #If the polyhedron has internal vertices that are not a part of the polyhedron (i.e. if the polyhedron does not divide the total network into to components)
            if not _IsDivided(fragment):
                #If the fragment does not contain any extra cycle whose all vertices belong to the fragment but the cycle is not a face,
                if not _ContainsExtraCycle(fragment):
                    #Add the fragment to the list.
                    #A fragment is a set of cycle IDs of the faces
                    fs = frozenset(fragment)
                    if fs not in _vitrites:
                        yield fragment
                        _vitrites.add(fs)
                else:
                    logger.debug("It contains extra cycles(s).")
            else:
                logger.debug("It has internal vertices.")
            #Search finished.
            return
        #If the perimeter is still open,
        for i in range(len(peri)):
            #If any vertex on the perimeter is shared by more than two faces,
            if numCyclesOnTheNode[peri[i]] > 2:
                logger.debug("#Failed(2)")
                return
        for i in range(len(peri)):
            #Look up the node on the perimeter which is shared by two faces.
            if numCyclesOnTheNode[peri[i]] == 2:
                #Reset the frag
                trynext = False
                #Three successive nodes around the node i
                center = peri[i]
                left   = peri[i-1]
                right  = peri[i+1-len(peri)] #Avoid to refer the out-of-list element
                #Reset the frag
                success = False
                logger.debug(f"Next triplet:{left} {center} {right}")
                if (left,center,right) in _cyclesAtATriplet:
                    logger.debug("Here cycles are:{0}".format(_cyclesAtATriplet[(left,center,right)]))
                    for cycleid in _cyclesAtATriplet[(left,center,right)]:
                        logger.debug(f"#Next:{cycleid}")
                        #if the cycle is new and its ID is larger than the origin,
                        if origin < cycleid and not cycleid in fragment:
                            nodes = _cycles[cycleid]
                            #Add the cycle as a face and extend the perimeter
                            newperi = _MergeCycles(peri, nodes, center,right)
                            logger.debug(f"#Result:{newperi}")
                            # result is not a simple cycle
                            if newperi == None:
                                trynext = True
                                logger.debug("#Try next!")
                            else:
                                for node in nodes:
                                    numCyclesOnTheNode[node] += 1
                                    mult = [numCyclesOnTheNode[i] for i in newperi]
                                    logger.debug(f"#{peri} {nodes} {edge} {newperi} {mult}")
                                yield from _Progress(origin, newperi, fragment | set([cycleid,]), numCyclesOnTheNode)
                                for node in nodes:
                                    numCyclesOnTheNode[node] -= 1
                                #if result == True:
                                #    return True
                #it might be too aggressive
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

    for cycleid, cycle in enumerate(_cycles):
        _RegisterTriplets(cycle,cycleid)
        _RegisterEdges(cycle,cycleid)
    #For counting the number of components separated by a polyhedral fragment
    _G = nx.Graph()

    for cycle in _cycles:
        nx.add_cycle(_G,cycle)
    _ncompo = nx.number_connected_components(_G)

    _vitrites = set()
    #The first cycle
    for cycleid in range(len(_cycles)):
        peri = _cycles[cycleid]
        fragment = set([cycleid])
        edge = tuple(peri[0:2])
        numCyclesOnTheNode = defaultdict(int)
        #increment the number-of-cycles-at-a-node counter
        #for each node on the first cycle.
        for node in peri:
            numCyclesOnTheNode[node] = 1
            logger.debug("#Candid: {0} {1}".format(cycleid,_cyclesAtAnEdge[edge]))
        #The second cycle, which is adjacent to the first one.
        for cycleid2 in _cyclesAtAnEdge[edge]:
            #The second one must have larger cycle ID than the first one.
            if cycleid < cycleid2:
                nodes = _cycles[cycleid2]
                #Make the perimeter of two cycles.
                newperi = _MergeCycles(peri, nodes, edge[0],edge[1])
                if newperi != None:
                    #increment the number-of-cycles-at-a-node counter
                    #for each node on the second cycle.
                    for node in nodes:
                        numCyclesOnTheNode[node] += 1
                        mult = [numCyclesOnTheNode[i] for i in newperi]
                        logger.debug("{0} {1} {2} {3} {4}".format(peri, nodes, edge, newperi,mult))
                    #Expand the perimeter by adding new faces to the polyhedron.
                    yield from _Progress(cycleid, newperi, set([cycleid,cycleid2]), numCyclesOnTheNode)
                    #decrement the number-of-cycles-at-a-node counter
                    #for each node on the second cycle.
                    for node in nodes:
                        numCyclesOnTheNode[node] -= 1
    return _vitrites


def test():
    g = nx.Graph()
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
    A = [cycle for cycle in cycles_iter(g, 4, pos=coord)]
    print(f"Number of cycles (PBC compliant): {len(A)}")
    vitrites = [v for v in polyhedra_iter(A)]
    print(f"Number of cubes: {len(vitrites)}")


if __name__ == "__main__":
    test()
