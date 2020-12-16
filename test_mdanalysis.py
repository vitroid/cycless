import MDAnalysis as mda
import cycless.cycles
import cycless.polyhed
import pairlist
import numpy as np
import networkx as nx

def water_HB(waters, cellmat):
    dg = nx.DiGraph()
    celli   = np.linalg.inv(cellmat)
    H = np.array([u.atoms.positions[atom.index] for water in waters for atom in water.atoms if atom.name == "H"], dtype=float)
    O = np.array([u.atoms.positions[atom.index] for water in waters for atom in water.atoms if atom.name == "O"], dtype=float)
    rH = H @ celli
    rO = O @ celli
    # HB is O-H distance is closer than 2.45 AA
    # Matsumoto JCP 2007 https://doi.org/10.1063/1.2431168
    for i,j,d in pairlist.pairs_iter(rH, 2.45, cellmat, pos2=rO):
        # but not in the same molecule
        if 1 < d:
            # label of the molecule where Hydrogen i belongs.
            imol = i // 2
            # H to O vector
            dg.add_edge(imol, j, vec=rO[j] - rH[i])
    return dg, rO


# Unfortunately, MDAnalysis do not read the concatenated gro file.
traj = open("npt_trjconv.gro")
while True:
    u = mda.Universe(traj)
    # cell dimension a,b,c,A,B,G
    # Note: length unit of MDAnalysis is AA, not nm.
    dimen   = u.trajectory.ts.dimensions
    # cell matrix (might be transposed)
    cellmat = mda.lib.mdamath.triclinic_vectors(dimen)
    # Pick up water molecules only
    waters = [residue for residue in u.residues if residue.resname[:3] == "SOL"]

    # make a graph of hydrogen bonds and fractional coordinate of its vertices
    dg, rO = water_HB(waters, cellmat)
    # undirected graph
    g = nx.Graph(dg)
    # detect the pentagons and hexagons.
    cycles = [cycle for cycle in cycless.cycles.cycles_iter(g, maxsize=6, pos=rO) if len(cycle) > 4]
    # detect the cages with number of faces between 12 and 16.
    cages  = [cage for cage in cycless.polyhed.polyhedra_iter(cycles, maxnfaces=16) if len(cage) > 11]
    for cage in cages:
        print(len(cage), cage)
