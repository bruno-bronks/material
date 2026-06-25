from app.agent.state import MaterialState


def node_ranker(state: MaterialState) -> dict:
    """Ordena candidatos por estabilidade e densidade (proxy local para custo/temperatura)."""
    materials = state.get("materials") or []

    def score(material: dict) -> tuple[float, float]:
        # Prioriza sinal de estabilidade real (banco de dados/DFT): energy_above_hull (Materials
        # Project), stability (OQMD), formation_energy (AFLOW). Só cai pra energia de formação
        # prevista pelo GNN quando nenhum desses existe — nunca mistura previsão de modelo com
        # dado real na mesma comparação como se tivessem a mesma confiança.
        stability_signal = material.get("energy_above_hull")
        if stability_signal is None:
            stability_signal = material.get("stability")
        if stability_signal is None:
            stability_signal = material.get("formation_energy")
        if stability_signal is None:
            stability_signal = material.get("gnn_formation_energy_ev_atom")

        stability_penalty = abs(stability_signal) if stability_signal is not None else float("inf")
        density = material.get("density") or 0
        return (stability_penalty, density)

    ranking = sorted(materials, key=score)
    return {"ranking": ranking[:5]}
