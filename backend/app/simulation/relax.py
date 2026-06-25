from dataclasses import dataclass

import numpy as np
from pymatgen.core import Structure

from app.gnn.potential import get_m3gnet_potential

MAX_ATOMS = 120


@dataclass
class RelaxationResult:
    converged: bool
    steps: int
    initial_energy_ev_atom: float
    final_energy_ev_atom: float
    max_force_ev_a: float
    volume_change_pct: float
    final_structure: Structure


def relax_structure(structure: Structure, fmax: float = 0.05, steps: int = 300) -> RelaxationResult | None:
    """V4: executa uma relaxação estrutural de verdade (não é previsão de propriedade).

    Usa o M3GNet como potencial interatômico no lugar de DFT real (Quantum
    ESPRESSO) — mesma ideia de "AI for Science" do V2/V3, aplicada a uma
    simulação (otimização de geometria) em vez de uma predição direta de
    propriedade.
    """
    if len(structure) > MAX_ATOMS:
        return None

    from matgl.ext.ase import Relaxer

    try:
        relaxer = Relaxer(potential=get_m3gnet_potential(), relax_cell=True)
        result = relaxer.relax(structure, fmax=fmax, steps=steps, verbose=False)
    except Exception:
        return None

    n_atoms = len(structure)
    trajectory = result["trajectory"]
    final_structure = result["final_structure"]
    max_force = float(np.abs(trajectory.forces[-1]).max())

    return RelaxationResult(
        converged=max_force <= fmax,
        steps=len(trajectory.energies),
        initial_energy_ev_atom=float(trajectory.energies[0]) / n_atoms,
        final_energy_ev_atom=float(trajectory.energies[-1]) / n_atoms,
        max_force_ev_a=max_force,
        volume_change_pct=(final_structure.volume - structure.volume) / structure.volume * 100,
        final_structure=final_structure,
    )
