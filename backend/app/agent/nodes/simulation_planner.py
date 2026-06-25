from pymatgen.core import Structure

from app.agent.state import MaterialState
from app.gnn.predictor import predict_band_gap, predict_formation_energy
from app.simulation.relax import relax_structure


def node_simulation_planner(state: MaterialState) -> dict:
    """V5: decide e executa as simulações disponíveis (GNN + relaxação) no candidato hipotético."""
    cif = state.get("candidate_structure_cif")
    if not cif:
        return {"discovery_metrics": {}}

    structure = Structure.from_str(cif, fmt="cif")
    metrics: dict = {}

    # A energia de formação já foi calculada na etapa de ranking do pool (V6 lite / active
    # learning, em node_hypothesis/node_reflection) — reaproveita em vez de recomputar.
    cached_energy = (state.get("discovery_metrics") or {}).get("gnn_formation_energy_ev_atom")
    formation_energy = cached_energy if cached_energy is not None else predict_formation_energy(structure)
    if formation_energy is not None:
        metrics["gnn_formation_energy_ev_atom"] = formation_energy

    # Candidato hipotético não tem band gap real em nenhum banco — só a previsão do GNN existe.
    band_gap = predict_band_gap(structure)
    if band_gap is not None:
        metrics["gnn_band_gap_ev"] = band_gap

    relaxation = relax_structure(structure)
    if relaxation is not None:
        metrics["relax_converged"] = relaxation.converged
        metrics["relax_max_force_ev_a"] = relaxation.max_force_ev_a
        metrics["relax_energy_change_ev_atom"] = (
            relaxation.final_energy_ev_atom - relaxation.initial_energy_ev_atom
        )
        metrics["relax_volume_change_pct"] = relaxation.volume_change_pct
    else:
        metrics["relax_converged"] = False
        metrics["relax_skipped_reason"] = "estrutura grande demais ou relaxação não convergiu"

    return {"discovery_metrics": metrics}
