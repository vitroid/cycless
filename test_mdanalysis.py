import MDAnalysis as mda
from cycless.cycles import cycles_iter, centerOfMass
from cycless.polyhed import polyhedra_iter
import pairlist
import numpy as np
import networkx as nx


def water_HB_digraph(waters, cellmat):
    dg = nx.DiGraph()
    celli = np.linalg.inv(cellmat)
    H = np.array([u.atoms.positions[atom.index]
                 for water in waters for atom in water.atoms if atom.name == "H"], dtype=float)
    O = np.array([u.atoms.positions[atom.index]
                 for water in waters for atom in water.atoms if atom.name == "O"], dtype=float)
    # In a fractional coordinate
    rH = H @ celli
    rO = O @ celli
    # O-H distance is closer than 2.45 AA
    # Matsumoto JCP 2007 https://doi.org/10.1063/1.2431168
    for i, j, d in pairlist.pairs_iter(rH, 2.45, cellmat, pos2=rO):
        # but distance is greater than 1 AA (i.e. O and H are not in the same
        # molecule)
        if 1 < d:
            # label of the molecule where Hydrogen i belongs.
            imol = i // 2
            # H to O vector
            # vec attribute is useful when you use cycless.dicycles.
            dg.add_edge(imol, j, vec=rO[j] - rH[i])
    return dg, rO


# Unfortunately, MDAnalysis does not read the concatenated gro file.
# https://docs.mdanalysis.org/stable/documentation_pages/coordinates/GRO.html
traj = open("npt_trjconv.gro")

u = mda.Universe(traj)
# cell dimension a,b,c,A,B,G
# Note: length unit of MDAnalysis is AA, not nm.
dimen = u.trajectory.ts.dimensions
# cell matrix (might be transposed)
cellmat = mda.lib.mdamath.triclinic_vectors(dimen)
# Pick up water molecules only
waters = [residue for residue in u.residues if residue.resname[:3] == "SOL"]

# make a graph of hydrogen bonds and fractional coordinate of its vertices
dg, rO = water_HB_digraph(waters, cellmat)
# undirected graph
g = nx.Graph(dg)
# detect the pentagons and hexagons.
cycles = [cycle for cycle in cycles_iter(
    g, maxsize=6, pos=rO) if len(cycle) > 4]

# Center of a cycle.
cycle_pos = np.array([centerOfMass(cycle, rO) for cycle in cycles]) @ cellmat

# detect the cages with number of faces between 12 and 16.
cages = [cage for cage in polyhedra_iter(
    cycles, maxnfaces=16) if len(cage) > 11]

# Center of a cage
cage_pos = []
for cage in cages:
    memb = set()
    for cycid in cage:
        memb |= set(cycles[cycid])
    cage_pos.append(centerOfMass(list(memb), rO))
cage_pos = np.array(cage_pos) @ cellmat

# or a one-liner
cage_pos = np.array([centerOfMass(list(set(
    [v for cycid in cage for v in cycles[cycid]])), rO) for cage in cages]) @ cellmat

for cage, pos in zip(cages, cage_pos):
    print(f"{len(cage)}-hedron@{pos}")
