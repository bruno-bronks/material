from app.agent.nodes.discovery_common import find_seed, propose_target_element, rank_candidate_pool
from app.agent.state import MaterialState

MAX_ITERATIONS = 3


def node_hypothesis(state: MaterialState) -> dict:
    """V5/V6 lite: acha um material real como base, decide (LLM) qual elemento substituir, e
    ranqueia candidatos quimicamente plausíveis por estabilidade prevista (GNN) antes de testar."""
    question = state["user_question"]

    seed = find_seed(question)
    if seed is None:
        return {
            "discovery_verdict": {
                "accepted": False,
                "reasons": [
                    "Não foi possível encontrar um material base no Materials Project "
                    "para esta pergunta (sem MP_API_KEY ou composição não encontrada)."
                ],
            },
            "discovery_iteration": 0,
            "discovery_max_iterations": 0,
            "discovery_log": [],
        }

    material_id, structure = seed
    base_composition = structure.composition.reduced_formula
    available_elements = ", ".join(sorted(str(el) for el in structure.composition.elements))

    target = propose_target_element(question, base_composition, material_id, available_elements)
    pool = rank_candidate_pool(structure, target.element_from)

    if not pool:
        return {
            "discovery_verdict": {
                "accepted": False,
                "reasons": [f"Nenhum candidato quimicamente plausível encontrado para substituir {target.element_from}."],
            },
            "discovery_iteration": 0,
            "discovery_max_iterations": 0,
            "discovery_log": [],
        }

    top, *remaining = pool

    return {
        "seed_material_id": material_id,
        "base_composition": base_composition,
        "available_elements": available_elements,
        "substitution": {
            "element_from": target.element_from,
            "element_to": top["element_to"],
            "justification": (
                f"{target.rationale} Escolhido por ranking de estabilidade prevista (GNN) entre "
                f"{len(pool)} candidatos quimicamente plausíveis (energia de formação prevista: "
                f"{top['gnn_formation_energy_ev_atom']:.3f} eV/átomo)."
            ),
        },
        "discovery_metrics": {"gnn_formation_energy_ev_atom": top["gnn_formation_energy_ev_atom"]},
        "candidate_pool": remaining,
        "discovery_iteration": 1,
        "discovery_max_iterations": MAX_ITERATIONS,
        "discovery_log": [],
    }
