from typing import TypedDict


class MaterialState(TypedDict, total=False):
    session_id: str
    user_question: str
    intent: str
    constraints: str
    objectives: list[str]
    context: dict
    materials: list[dict]
    papers: list[dict]
    simulations: list[dict]
    candidates: list[dict]
    ranking: list[dict]
    raw_answer: str
    report: str

    # V5 — Scientific Agent (material_discovery): hipótese -> geração -> simulação -> crítica,
    # com loop de reflexão. Nunca guarda objetos pymatgen.Structure aqui — só dados serializáveis
    # (a estrutura candidata vira CIF, que cada node reconstrói quando precisa).
    seed_material_id: str
    base_composition: str
    available_elements: str
    substitution: dict
    candidate_pool: list[dict]  # V6 lite: candidatos restantes, ranqueados por GNN (active learning)
    candidate_structure_cif: str
    candidate_composition: str
    discovery_metrics: dict
    discovery_verdict: dict
    discovery_iteration: int
    discovery_max_iterations: int
    discovery_log: list[dict]
