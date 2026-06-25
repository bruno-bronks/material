from pymatgen.analysis.eos import EOS, EOSError
from pymatgen.core import Structure

from app.gnn.potential import get_m3gnet_potential

EV_PER_A3_TO_GPA = 160.21766208
VOLUME_SCALE_FACTORS = (0.94, 0.97, 1.0, 1.03, 1.06)
MAX_ATOMS = 40


def estimate_bulk_modulus(structure: Structure) -> float | None:
    """Módulo de compressibilidade (GPa) via equação de estado com M3GNet.

    Relaxa a estrutura em volumes ligeiramente diferentes do de equilíbrio
    (célula fixa, só posições atômicas) e ajusta uma equação de estado de
    Birch-Murnaghan à curva energia x volume — um substituto barato para o
    que normalmente seria feito com vários cálculos de DFT.
    """
    if len(structure) > MAX_ATOMS:
        return None

    from matgl.ext.ase import Relaxer

    try:
        relaxer = Relaxer(potential=get_m3gnet_potential(), relax_cell=False)
        volumes, energies = [], []
        for factor in VOLUME_SCALE_FACTORS:
            scaled = structure.copy()
            scaled.scale_lattice(structure.volume * factor)
            result = relaxer.relax(scaled, fmax=0.1, steps=200, verbose=False)
            volumes.append(scaled.volume)
            energies.append(float(result["trajectory"].energies[-1]))

        eos = EOS(eos_name="birch_murnaghan").fit(volumes, energies)
        return float(eos.b0) * EV_PER_A3_TO_GPA
    except (EOSError, RuntimeError, ValueError):
        return None
