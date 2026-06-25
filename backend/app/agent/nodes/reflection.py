from app.agent.state import MaterialState


def node_reflection(state: MaterialState) -> dict:
    """V6 lite (active learning): avança pro próximo candidato do pool já ranqueado por
    estabilidade prevista (GNN) na etapa de hipótese — sem nova chamada de LLM."""
    pool = state.get("candidate_pool") or []
    if not pool:
        return {"discovery_iteration": state.get("discovery_iteration", 1) + 1}

    substitution = state.get("substitution") or {}
    top, *remaining = pool

    return {
        "substitution": {
            "element_from": substitution.get("element_from"),
            "element_to": top["element_to"],
            "justification": (
                "Próximo candidato do pool, ranqueado por energia de formação prevista (GNN): "
                f"{top['gnn_formation_energy_ev_atom']:.3f} eV/átomo."
            ),
        },
        "discovery_metrics": {"gnn_formation_energy_ev_atom": top["gnn_formation_energy_ev_atom"]},
        "candidate_pool": remaining,
        "discovery_iteration": state.get("discovery_iteration", 1) + 1,
    }
