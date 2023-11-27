from genice2.genice import GenIce
from genice2.plugin import Lattice, Format, Molecule
import cycless.dicycles as dc

# Generate an ice I structure as a directed graph
lattice = Lattice("1h")
formatter = Format("raw", stage=(3,))
raw = GenIce(lattice, signature="ice 1h", rep=[2, 2, 2]).generate_ice(formatter)

for cycle in dc.dicycles_iter(raw["digraph"], size=6):
    print(cycle)
