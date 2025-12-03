from genice2.genice import GenIce
from genice2.plugin import Lattice, Format, Molecule
from cycless.rings import rings_iter

# Generate an ice I structure as a directed graph
lattice = Lattice("1h")
formatter = Format("raw", stage=(4,))
raw = GenIce(lattice, signature="ice 1h", rep=[2, 2, 2]).generate_ice(formatter)

for ring in rings_iter(raw["digraph"], maxsize=6):
    print(ring)
